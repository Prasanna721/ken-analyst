# Ken Analyst - Web Application

Next.js application for Ken Analyst financial analysis platform.

## Getting Started

```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.local.example .env.local
# Edit .env.local with your API credentials

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

Open [http://localhost:3000](http://localhost:3000) to view the application.

## Environment Variables

Create `.env.local` file:

```
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
NEXT_PUBLIC_HASHED_API_SECRET=your_hashed_api_secret_here
```

To generate the hashed API secret (SHA256 hash of your API_SECRET):
```bash
cd ../api
.venv/bin/python -c "import hashlib; print(hashlib.sha256('YOUR_API_SECRET'.encode()).hexdigest())"
```

## Project Structure

```
web/
├── app/
│   ├── fonts.ts          # Font configuration
│   ├── globals.css       # Global styles & theme
│   ├── layout.tsx        # Root layout with font setup
│   └── page.tsx          # Homepage with two-column layout
├── components/
│   ├── Header.tsx        # Header with "Ken" branding
│   ├── Layout.tsx        # Page layout wrapper
│   ├── SearchBox.tsx     # Company search component
│   └── WorkspaceList.tsx # Workspace list component
├── lib/
│   └── api.ts            # API client functions
└── public/
    └── fonts/            # Custom font files
```

## Design System

### Theme: Light Minimalist
- Sharp corners (no border-radius)
- Light golden accents (#D4AF37, #F5E6D3)
- Minimal borders and ample whitespace
- Clean typography hierarchy

### Colors
- `golden` - Accent color (light, default, dark)
- `background` - Primary and secondary backgrounds
- `text` - Primary and secondary text
- `border` - Border color

## Fonts

- **Heading**: Instrument Serif (used for "Ken" branding and headings)
- **Body**: Monument Grotesk Mono (regular, medium, bold weights)

## Adding New Pages

Create new page files in the `app/` directory following Next.js App Router conventions.

```tsx
import Layout from "@/components/Layout";

export default function NewPage() {
  return (
    <Layout>
      <div className="h-full p-8">
        {/* Your content */}
      </div>
    </Layout>
  );
}
```
