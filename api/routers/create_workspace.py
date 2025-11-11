from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from database import get_db
from models import WorkspaceCreate, DocumentCreate, ActivityCreate, ParsedDocumentCreate, APIResponse
from services import workspace_service, documents_service, activity_service, parsed_documents_service
from services.filings_service import download_filings, extract_dates
import os
import shutil
import zipfile
import json
from pathlib import Path
from typing import Optional
from landingai_ade import LandingAIADE

router = APIRouter(tags=["workspace"])

def flatten_and_copy_files(source_dir: str, dest_dir: str):
    """Recursively flatten directory structure and copy all files to dest_dir"""
    files_copied = []

    for root, dirs, files in os.walk(source_dir):
        for file in files:
            source_file = os.path.join(root, file)
            # Create unique filename if there's a collision
            dest_file = os.path.join(dest_dir, file)
            counter = 1
            base_name, ext = os.path.splitext(file)
            while os.path.exists(dest_file):
                dest_file = os.path.join(dest_dir, f"{base_name}_{counter}{ext}")
                counter += 1

            shutil.copy2(source_file, dest_file)
            files_copied.append(dest_file)

    return files_copied

def extract_zip(zip_path: str, extract_dir: str):
    """Extract zip file to directory"""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

def parse_document_with_landingai(file_path: str, workspace_id: str, document_id: str, db: Session):
    """Parse document using LandingAI and save as JSON"""
    try:
        # Log parsing start
        activity_data = ActivityCreate(
            workspace_id=workspace_id,
            category="sub",
            status=200,
            title="Document Parsing",
            message=f"Started parsing {os.path.basename(file_path)}"
        )
        activity_service.create_activity(db, activity_data)

        # Initialize LandingAI client
        api_key = os.environ.get("LANDING_API_KEY")
        if not api_key:
            print(f"Warning: LANDING_API_KEY not found, skipping parse for {file_path}")
            return None

        client = LandingAIADE(
            apikey=api_key,
            environment="eu"
        )

        # Parse the document
        response = client.parse(
            document=Path(file_path),
            model="dpt-2-latest"
        )

        # Save response as JSON
        json_filename = os.path.splitext(file_path)[0] + ".json"
        with open(json_filename, 'w') as f:
            json.dump(response, f, indent=2)

        # Create parsed document entry with status=False initially
        parsed_doc_data = ParsedDocumentCreate(
            workspace_id=workspace_id,
            documents_id=document_id,
            filepath=json_filename,
            status=False
        )
        parsed_doc = parsed_documents_service.create_parsed_document(db, parsed_doc_data)

        # Update status to True (done parsing)
        from models import ParsedDocumentUpdate
        update_data = ParsedDocumentUpdate(status=True)
        parsed_documents_service.update_parsed_document(db, parsed_doc.id, update_data)

        # Log parsing completion
        activity_data = ActivityCreate(
            workspace_id=workspace_id,
            category="sub",
            status=200,
            title="Document Parsing",
            message=f"Completed parsing {os.path.basename(file_path)}"
        )
        activity_service.create_activity(db, activity_data)

        return parsed_doc.to_dict()

    except Exception as e:
        print(f"Error parsing document {file_path}: {str(e)}")
        # Log parsing error
        activity_data = ActivityCreate(
            workspace_id=workspace_id,
            category="sub",
            status=500,
            title="Document Parsing",
            message=f"Failed parsing {os.path.basename(file_path)}: {str(e)}"
        )
        activity_service.create_activity(db, activity_data)
        return None

def process_filings_for_workspace(ticker: str, workspace_id: str, form_type: str, db: Session):
    """Download filings and add to workspace"""
    ticker = ticker.upper()

    # Download filings to temp location
    temp_base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", f"temp_{ticker}")
    os.makedirs(temp_base_path, exist_ok=True)

    from sec_edgar_downloader import Downloader
    dl = Downloader("CompanyName", "email@example.com", temp_base_path)

    # Download based on form type
    if form_type == "10-K":
        dl.get("10-K", ticker, after="2015-01-01")
    else:
        dl.get("10-Q", ticker, after="2015-01-01")

    temp_form_folder = os.path.join(temp_base_path, "sec-edgar-filings", ticker, form_type)
    workspace_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", workspace_id)

    documents_added = []

    if os.path.exists(temp_form_folder):
        for filing_dir in os.listdir(temp_form_folder):
            filing_path = os.path.join(temp_form_folder, filing_dir)
            if os.path.isdir(filing_path):
                full_submission = os.path.join(filing_path, "full-submission.txt")
                if os.path.exists(full_submission):
                    # Extract dates
                    filing_date, reporting_date = extract_dates(full_submission)

                    # Copy file to workspace
                    dest_file = os.path.join(workspace_folder, f"{form_type}_{filing_dir}_full-submission.txt")
                    shutil.copy2(full_submission, dest_file)

                    # Format dates to YYYY/MM/DD
                    filing_date_formatted = f"{filing_date[:4]}/{filing_date[4:6]}/{filing_date[6:]}" if filing_date else None
                    reporting_date_formatted = f"{reporting_date[:4]}/{reporting_date[4:6]}/{reporting_date[6:]}" if reporting_date else None

                    # Add to documents table
                    doc_data = DocumentCreate(
                        workspace_id=workspace_id,
                        doc_type=form_type.replace("-", "_"),  # 10-Q -> 10_Q, 10-K -> 10_K
                        file_path=dest_file,
                        filing_date=filing_date_formatted,
                        reporting_date=reporting_date_formatted,
                        doc_id=filing_dir
                    )
                    document = documents_service.create_document(db, doc_data)
                    documents_added.append(document.to_dict())

                    # Log download activity
                    activity_data = ActivityCreate(
                        workspace_id=workspace_id,
                        category="sub",
                        status=200,
                        title="Filing Downloaded",
                        message=f"{filing_dir} downloaded"
                    )
                    activity_service.create_activity(db, activity_data)

    # Cleanup temp directory
    if os.path.exists(temp_base_path):
        shutil.rmtree(temp_base_path)

    return documents_added

@router.post("/create_workspace", response_model=APIResponse)
async def create_workspace_endpoint(
    workspace_id: Optional[str] = Form(None),
    ticker: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Create workspace with optional file upload and/or ticker-based filings

    - workspace_id: Optional workspace ID (auto-generated if not provided)
    - ticker: Optional ticker symbol to download 10-Q and 10-K filings
    - file: Optional file upload (can be zip or single file)
    """
    try:
        # Step 1: Create workspace via internal API
        workspace_data = WorkspaceCreate(
            id=workspace_id,
            name=None,  # Will be auto-generated
            ticker=ticker or "UNKNOWN"
        )
        workspace = workspace_service.create_workspace(db, workspace_data)
        created_workspace_id = workspace.id

        # Log main activity
        activity_data = ActivityCreate(
            workspace_id=created_workspace_id,
            category="main",
            status=200,
            title="Workspace Creation",
            message="Creating workspace"
        )
        activity_service.create_activity(db, activity_data)

        workspace_folder = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            created_workspace_id
        )

        result = {
            "workspace": workspace.to_dict(),
            "documents": []
        }

        # Step 2: Handle file upload if present
        if file:
            temp_dir = os.path.join(workspace_folder, "temp")
            os.makedirs(temp_dir, exist_ok=True)

            # Save uploaded file
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Check if it's a zip file
            if file.filename.endswith('.zip'):
                # Extract zip
                extract_dir = os.path.join(temp_dir, "extracted")
                os.makedirs(extract_dir, exist_ok=True)
                extract_zip(file_path, extract_dir)

                # Log unzip activity
                activity_data = ActivityCreate(
                    workspace_id=created_workspace_id,
                    category="sub",
                    status=200,
                    title="File Processing",
                    message=f"Unzipped {file.filename}"
                )
                activity_service.create_activity(db, activity_data)

                # Flatten and copy all files
                files_copied = flatten_and_copy_files(extract_dir, workspace_folder)
            else:
                # Single file - copy to workspace folder
                dest_file = os.path.join(workspace_folder, file.filename)
                shutil.copy2(file_path, dest_file)
                files_copied = [dest_file]

            # Add each file to documents table
            for file_path in files_copied:
                doc_data = DocumentCreate(
                    workspace_id=created_workspace_id,
                    doc_type="other",
                    file_path=file_path
                )
                document = documents_service.create_document(db, doc_data)
                result["documents"].append(document.to_dict())

            # Cleanup temp directory
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

        # Step 3: Handle ticker-based filings if present
        if ticker:
            # Download and process 10-Q filings
            docs_10q = process_filings_for_workspace(ticker, created_workspace_id, "10-Q", db)
            result["documents"].extend(docs_10q)

            # Download and process 10-K filings
            docs_10k = process_filings_for_workspace(ticker, created_workspace_id, "10-K", db)
            result["documents"].extend(docs_10k)

        # Step 4: Parse all documents using LandingAI
        for doc in result["documents"]:
            try:
                doc_id = doc.get("id")
                doc_file_path = doc.get("file_path")
                if doc_id and doc_file_path and os.path.exists(doc_file_path):
                    parse_document_with_landingai(doc_file_path, created_workspace_id, doc_id, db)
            except Exception as e:
                print(f"Error parsing document {doc.get('file_path')}: {str(e)}")
                continue

        return APIResponse(
            status=201,
            response=result
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
