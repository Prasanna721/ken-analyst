import os
import asyncio
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database import get_db
from models import APIResponse
from services import agent_service, agent_message_service
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import json

router = APIRouter(prefix="/agent", tags=["agent_query"])

class AgentQueryRequest(BaseModel):
    workspace_id: str
    agent_id: Optional[str] = None
    prompt: str
    chunk_id: Optional[str] = None
    chunk_content: Optional[str] = None

@router.post("/query/stream")
async def query_agent_stream(
    query_request: AgentQueryRequest,
    db: Session = Depends(get_db)
):
    """Stream agent responses using Claude Agent SDK"""

    async def generate():
        try:
            # Import here to avoid loading on startup
            from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, TextBlock, ResultMessage

            # Create or get agent
            agent_id = query_request.agent_id
            if not agent_id:
                from models import AgentCreate
                agent_data = AgentCreate(
                    workspace_id=query_request.workspace_id,
                    name=f"Analyst Ken - {query_request.chunk_id or 'General'}"
                )
                agent = agent_service.create_agent(db, agent_data)
                agent_id = agent.id

                # Send agent_id as first message
                yield f"data: {json.dumps({'type': 'agent_id', 'agent_id': agent_id})}\n\n"

            # Save user message
            from models import AgentMessageCreate
            user_msg = AgentMessageCreate(
                agent_id=agent_id,
                role="user",
                message=query_request.prompt
            )
            agent_message_service.create_message(db, user_msg)

            # Set working directory
            workspace_folder = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "data",
                query_request.workspace_id,
                "ai_agents",
                agent_id
            )
            os.makedirs(workspace_folder, exist_ok=True)

            # Configure options
            options = ClaudeAgentOptions(
                allowed_tools=["Read", "Write", "Bash"],
                permission_mode='acceptEdits',
                cwd=workspace_folder
            )

            # Build prompt with context
            full_prompt = query_request.prompt
            if query_request.chunk_content:
                full_prompt = f"Context from document chunk:\n\n{query_request.chunk_content}\n\nUser question: {query_request.prompt}"

            # Stream response
            async with ClaudeSDKClient(options=options) as client:
                await client.query(full_prompt)

                assistant_message = ""

                async for message in client.receive_messages():
                    if isinstance(message, AssistantMessage):
                        for block in message.content:
                            if isinstance(block, TextBlock):
                                # Stream text chunks
                                text = block.text
                                assistant_message += text
                                yield f"data: {json.dumps({'type': 'text', 'content': text})}\n\n"

                    elif isinstance(message, ResultMessage):
                        # Save assistant message to database
                        if assistant_message:
                            assistant_msg = AgentMessageCreate(
                                agent_id=agent_id,
                                role="assistant",
                                message=assistant_message
                            )
                            agent_message_service.create_message(db, assistant_msg)

                        # Send completion message
                        yield f"data: {json.dumps({'type': 'done'})}\n\n"
                        break

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            yield f"data: {json.dumps({'type': 'error', 'content': error_msg})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.post("/query")
async def query_agent(
    query_request: AgentQueryRequest,
    db: Session = Depends(get_db)
):
    """Non-streaming agent query"""
    try:
        # Import here to avoid loading on startup
        from claude_agent_sdk import query as claude_query, ClaudeAgentOptions, AssistantMessage, TextBlock

        # Create or get agent
        agent_id = query_request.agent_id
        if not agent_id:
            from models import AgentCreate
            agent_data = AgentCreate(
                workspace_id=query_request.workspace_id,
                name=f"Analyst Ken - {query_request.chunk_id or 'General'}"
            )
            agent = agent_service.create_agent(db, agent_data)
            agent_id = agent.id

        # Save user message
        from models import AgentMessageCreate
        user_msg = AgentMessageCreate(
            agent_id=agent_id,
            role="user",
            message=query_request.prompt
        )
        agent_message_service.create_message(db, user_msg)

        # Set working directory
        workspace_folder = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            query_request.workspace_id,
            "ai_agents",
            agent_id
        )
        os.makedirs(workspace_folder, exist_ok=True)

        # Configure options
        options = ClaudeAgentOptions(
            allowed_tools=["Read", "Write", "Bash"],
            permission_mode='acceptEdits',
            cwd=workspace_folder
        )

        # Build prompt with context
        full_prompt = query_request.prompt
        if query_request.chunk_content:
            full_prompt = f"Context from document chunk:\n\n{query_request.chunk_content}\n\nUser question: {query_request.prompt}"

        # Get response
        response_text = ""
        async for message in claude_query(prompt=full_prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        response_text += block.text

        # Save assistant message
        if response_text:
            assistant_msg = AgentMessageCreate(
                agent_id=agent_id,
                role="assistant",
                message=response_text
            )
            agent_message_service.create_message(db, assistant_msg)

        return APIResponse(
            status=200,
            response={
                "agent_id": agent_id,
                "response": response_text
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
