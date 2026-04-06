#!/usr/bin/env python3
"""
Local Static HTML Generator for GHEN Digital

Generates self-contained HTML files from markdown content with:
- Full SEO meta tags
- JSON-LD schema markup
- Responsive design
- Featured images
- FAQ sections

Usage:
    python tools/local_generator.py generate \
        --file .claude/doc/feature/copy-deliverable.md \
        --feature-name feature-name \
        --category "Lab"
"""

import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import markdown
    from markdown.extensions import extra, codehilite, tables, toc
except ImportError:
    print("Error: markdown library not installed.")
    print("Install with: pip install markdown")
    exit(1)


class LocalHTMLGenerator:
    """Generate static HTML from markdown content"""
    
    def __init__(self):
        self.site_url = "https://ghendigital.com/workshop-agentes-ia/"
        self.author_name = "expert-ia"
        self.site_name = "GHEN Digital"
        
    def parse_copy_deliverable(self, filepath: str) -> Dict:
        """Extract metadata and content from copy deliverable"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract SEO meta section
        seo_meta_pattern = r'## SEO Meta\s*\n(.*?)(?=\n##|\Z)'
        seo_match = re.search(seo_meta_pattern, content, re.DOTALL)
        
        metadata = {
            'seo_title': '',
            'meta_description': '',
            'focus_keyword': '',
            'slug': '',
            'category': '',
            'tags': []
        }
        
        if seo_match:
            seo_section = seo_match.group(1)
            
            # Extract Page title
            title_match = re.search(r'\*\*Page title:\*\*\s*(.+)', seo_section)
            if title_match:
                metadata['seo_title'] = title_match.group(1).strip()
            
            # Extract Meta description
            desc_match = re.search(r'\*\*Meta description:\*\*\s*(.+)', seo_section)
            if desc_match:
                metadata['meta_description'] = desc_match.group(1).strip()
            
            # Extract Focus keyword
            keyword_match = re.search(r'\*\*(?:Rank Math focus keyword|Focus keyword):\*\*\s*(.+)', seo_section)
            if keyword_match:
                metadata['focus_keyword'] = keyword_match.group(1).strip()
            
            # Extract Slug
            slug_match = re.search(r'\*\*Slug:\*\*\s*(.+)', seo_section)
            if slug_match:
                metadata['slug'] = slug_match.group(1).strip()
            
            # Extract Category
            cat_match = re.search(r'\*\*Category:\*\*\s*(.+)', seo_section)
            if cat_match:
                metadata['category'] = cat_match.group(1).strip()
            
            # Extract Tags
            tags_match = re.search(r'\*\*Tags:\*\*\s*(.+)', seo_section)
            if tags_match:
                tags_str = tags_match.group(1).strip()
                metadata['tags'] = [t.strip() for t in tags_str.split(',')]
        
        # Extract H1 (first # heading in content)
        h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        metadata['h1'] = h1_match.group(1).strip() if h1_match else metadata['seo_title']
        
        # Extract main content (everything before SEO Meta section)
        if seo_match:
            main_content = content[:seo_match.start()].strip()
        else:
            main_content = content
        
        # Extract FAQ section if present
        faq_pattern = r'##\s+(?:Preguntas frecuentes|FAQ).*?\n(.*?)(?=\n##[^#]|\Z)'
        faq_match = re.search(faq_pattern, main_content, re.DOTALL | re.IGNORECASE)
        
        if faq_match:
            metadata['faq_content'] = faq_match.group(0)
            metadata['faq_items'] = self.parse_faq(faq_match.group(1))
        else:
            metadata['faq_content'] = None
            metadata['faq_items'] = []
        
        metadata['main_content'] = main_content
        
        return metadata
    
    def parse_faq(self, faq_text: str) -> List[Dict]:
        """Parse FAQ section into Q&A pairs"""
        faq_items = []
        
        # Pattern: ### Question followed by answer paragraphs
        questions = re.finditer(r'###\s+(.+?)\n\n(.*?)(?=\n###|\Z)', faq_text, re.DOTALL)
        
        for match in questions:
            question = match.group(1).strip()
            answer = match.group(2).strip()
            
            faq_items.append({
                'question': question,
                'answer': answer
            })
        
        return faq_items
    
    def markdown_to_html(self, markdown_text: str) -> str:
        """Convert markdown to HTML with extensions"""
        html = markdown.markdown(
            markdown_text,
            extensions=['extra', 'codehilite', 'tables', 'toc']
        )
        return html
    
    def generate_article_schema(self, metadata: Dict, featured_image: str) -> Dict:
        """Generate Article JSON-LD schema"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        return {
            "@type": "Article",
            "headline": metadata['h1'],
            "description": metadata['meta_description'],
            "author": {
                "@type": "Person",
                "name": self.author_name,
                "url": f"{self.site_url}about/"
            },
            "publisher": {
                "@type": "Organization",
                "name": self.site_name,
                "url": self.site_url,
                "logo": {
                    "@type": "ImageObject",
                    "url": f"{self.site_url}logo.png"
                }
            },
            "datePublished": today,
            "dateModified": today,
            "image": featured_image,
            "articleSection": metadata.get('category', 'Blog'),
            "keywords": metadata.get('focus_keyword', '')
        }
    
    def generate_breadcrumb_schema(self, metadata: Dict) -> Dict:
        """Generate BreadcrumbList JSON-LD schema"""
        category = metadata.get('category', 'Blog')
        category_slug = category.lower().replace(' ', '-')
        
        return {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": "Inicio",
                    "item": self.site_url
                },
                {
                    "@type": "ListItem",
                    "position": 2,
                    "name": category,
                    "item": f"{self.site_url}{category_slug}/"
                },
                {
                    "@type": "ListItem",
                    "position": 3,
                    "name": metadata['h1'],
                    "item": f"{self.site_url}{metadata.get('slug', '')}"
                }
            ]
        }
    
    def generate_faq_schema(self, faq_items: List[Dict]) -> Dict:
        """Generate FAQPage JSON-LD schema"""
        if not faq_items:
            return None
        
        main_entity = []
        for item in faq_items:
            main_entity.append({
                "@type": "Question",
                "name": item['question'],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": item['answer']
                }
            })
        
        return {
            "@type": "FAQPage",
            "mainEntity": main_entity
        }
    
    def render_faq_html(self, faq_items: List[Dict]) -> str:
        """Render FAQ section as HTML"""
        if not faq_items:
            return ""
        
        html = '<div class="faq-section">\n'
        html += '  <h2>Preguntas frecuentes</h2>\n'
        
        for item in faq_items:
            html += '  <div class="faq-item">\n'
            html += f'    <h3 class="faq-question">{item["question"]}</h3>\n'
            html += f'    <div class="faq-answer">{self.markdown_to_html(item["answer"])}</div>\n'
            html += '  </div>\n'
        
        html += '</div>\n'
        return html
    
    def generate_html(
        self,
        metadata: Dict,
        featured_image_path: str,
        output_dir: Path
    ) -> str:
        """Generate complete HTML file"""
        
        # Convert main content to HTML
        main_html = self.markdown_to_html(metadata['main_content'])
        
        # Generate schemas
        schema_graph = [
            self.generate_article_schema(metadata, f"./assets/featured.jpg"),
            self.generate_breadcrumb_schema(metadata)
        ]
        
        # Add FAQ schema if present
        faq_schema = self.generate_faq_schema(metadata.get('faq_items', []))
        if faq_schema:
            schema_graph.append(faq_schema)
        
        schema_json = json.dumps({
            "@context": "https://schema.org",
            "@graph": schema_graph
        }, indent=2, ensure_ascii=False)
        
        # Render FAQ HTML
        faq_html = self.render_faq_html(metadata.get('faq_items', []))
        
        # Canonical URL
        canonical_url = f"{self.site_url}{metadata.get('slug', '')}"
        
        # Date
        today = datetime.now().strftime('%d %B %Y')
        
        # Build complete HTML
        html_template = f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <!-- SEO Meta Tags -->
    <title>{metadata['seo_title']}</title>
    <meta name="description" content="{metadata['meta_description']}">
    <meta name="keywords" content="{metadata['focus_keyword']}">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="{canonical_url}">
    
    <!-- Open Graph -->
    <meta property="og:title" content="{metadata['seo_title']}">
    <meta property="og:description" content="{metadata['meta_description']}">
    <meta property="og:type" content="article">
    <meta property="og:url" content="{canonical_url}">
    <meta property="og:image" content="./assets/featured.jpg">
    <meta property="og:site_name" content="{self.site_name}">
    
    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{metadata['seo_title']}">
    <meta name="twitter:description" content="{metadata['meta_description']}">
    <meta name="twitter:image" content="./assets/featured.jpg">
    
    <!-- JSON-LD Schema Markup -->
    <script type="application/ld+json">
{schema_json}
    </script>
    
    <!-- Embedded Styles -->
    <style>
        /* Base Reset */
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        /* Typography */
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, "Helvetica Neue", sans-serif;
            font-size: 18px;
            line-height: 1.7;
            color: #2c3e50;
            background: #ffffff;
            max-width: 100%;
            overflow-x: hidden;
        }}
        
        /* Container */
        .container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem 1.5rem;
        }}
        
        /* Header */
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 3rem 0;
            text-align: center;
            margin-bottom: 3rem;
        }}
        
        header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            line-height: 1.2;
        }}
        
        .meta {{
            font-size: 0.95rem;
            opacity: 0.9;
        }}
        
        /* Featured Image */
        .featured-image {{
            width: 100%;
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        /* Typography */
        h2 {{
            font-size: 1.8rem;
            margin-top: 2.5rem;
            margin-bottom: 1rem;
            color: #1a202c;
            font-weight: 600;
        }}
        
        h3 {{
            font-size: 1.4rem;
            margin-top: 2rem;
            margin-bottom: 0.8rem;
            color: #2d3748;
            font-weight: 600;
        }}
        
        p {{
            margin-bottom: 1.2rem;
        }}
        
        strong {{
            font-weight: 600;
            color: #1a202c;
        }}
        
        /* Lists */
        ul, ol {{
            margin-bottom: 1.5rem;
            padding-left: 2rem;
        }}
        
        li {{
            margin-bottom: 0.5rem;
        }}
        
        /* Code */
        code {{
            background: #f7fafc;
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
            font-size: 0.9em;
            font-family: "Courier New", monospace;
            color: #e53e3e;
        }}
        
        pre {{
            background: #2d3748;
            color: #e2e8f0;
            padding: 1.5rem;
            border-radius: 8px;
            overflow-x: auto;
            margin-bottom: 1.5rem;
        }}
        
        pre code {{
            background: transparent;
            color: inherit;
            padding: 0;
        }}
        
        /* Tables */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 2rem;
            overflow-x: auto;
            display: block;
        }}
        
        th, td {{
            border: 1px solid #e2e8f0;
            padding: 0.75rem;
            text-align: left;
        }}
        
        th {{
            background: #f7fafc;
            font-weight: 600;
        }}
        
        /* FAQ Section */
        .faq-section {{
            background: #f7fafc;
            padding: 2rem;
            border-radius: 8px;
            margin: 2rem 0;
        }}
        
        .faq-item {{
            margin-bottom: 1.5rem;
        }}
        
        .faq-question {{
            font-size: 1.2rem;
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 0.5rem;
        }}
        
        .faq-answer {{
            color: #4a5568;
            line-height: 1.6;
        }}
        
        .faq-answer p {{
            margin-bottom: 0.8rem;
        }}
        
        /* Links */
        a {{
            color: #667eea;
            text-decoration: none;
            border-bottom: 1px solid transparent;
            transition: border-color 0.2s;
        }}
        
        a:hover {{
            border-bottom-color: #667eea;
        }}
        
        /* Footer */
        footer {{
            margin-top: 4rem;
            padding: 2rem 0;
            border-top: 1px solid #e2e8f0;
            text-align: center;
            color: #718096;
            font-size: 0.9rem;
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            body {{ font-size: 16px; }}
            header h1 {{ font-size: 1.8rem; }}
            h2 {{ font-size: 1.5rem; }}
            h3 {{ font-size: 1.2rem; }}
            .container {{ padding: 1rem; }}
        }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>{metadata['h1']}</h1>
            <div class="meta">
                <span>{metadata.get('category', 'Blog')}</span> • 
                <span>{today}</span> • 
                <span>{self.author_name}</span>
            </div>
        </div>
    </header>
    
    <main class="container">
        <img src="assets/featured.jpg" alt="{metadata['h1']}" class="featured-image">
        
        <!-- Main Content -->
        {main_html}
        
        <!-- FAQ Section -->
        {faq_html}
    </main>
    
    <footer>
        <div class="container">
            <p>&copy; 2026 {self.site_name} | <a href="{self.site_url}">Workshop Agentes IA</a></p>
        </div>
    </footer>
</body>
</html>'''
        
        return html_template
    
    def generate(
        self,
        copy_file: str,
        feature_name: str,
        category: str = "Lab"
    ) -> Tuple[Path, str]:
        """
        Main generation method
        
        Returns:
            (output_dir, html_path)
        """
        # Parse copy deliverable
        print(f"📄 Parsing {copy_file}...")
        metadata = self.parse_copy_deliverable(copy_file)
        metadata['category'] = category
        
        # Create output directory
        output_dir = Path(f"outputs/html/{feature_name}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        assets_dir = output_dir / "assets"
        assets_dir.mkdir(exist_ok=True)
        
        print(f"📁 Output directory: {output_dir}")
        
        # Check for featured image
        featured_image = assets_dir / "featured.jpg"
        if not featured_image.exists():
            print(f"⚠️  Featured image not found: {featured_image}")
            print(f"   Generate it with: python tools/image_generator.py generate --output {featured_image}")
        
        # Generate HTML
        print("🔨 Generating HTML...")
        html_content = self.generate_html(metadata, str(featured_image), output_dir)
        
        # Save HTML
        html_path = output_dir / "index.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML generated: {html_path}")
        
        # Create README
        readme_content = f"""# {metadata['h1']}

## Generated Files

- `index.html` — Main HTML file
- `assets/featured.jpg` — Featured image

## Metadata

- **SEO Title:** {metadata['seo_title']}
- **Meta Description:** {metadata['meta_description']}
- **Focus Keyword:** {metadata['focus_keyword']}
- **Category:** {metadata.get('category', 'Blog')}
- **Slug:** {metadata.get('slug', '')}

## Schema Included

- `Article` — Article schema
- `BreadcrumbList` — Breadcrumb navigation
{f"- `FAQPage` — FAQ schema ({len(metadata.get('faq_items', []))} questions)" if metadata.get('faq_items') else ""}

## How to View

Open `index.html` in any browser.

Or use Python's HTTP server:
```bash
cd {output_dir}
python -m http.server 8000
```
Then visit: http://localhost:8000

## Validation

- HTML: https://validator.w3.org/
- Schema: https://search.google.com/test/rich-results
- Mobile: https://search.google.com/test/mobile-friendly

---
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        readme_path = output_dir / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"📝 README created: {readme_path}")
        print(f"\n🎉 Complete! Open {html_path} in your browser.")
        
        return output_dir, str(html_path)


def main():
    parser = argparse.ArgumentParser(
        description='Generate static HTML from markdown content'
    )
    
    parser.add_argument(
        'command',
        choices=['generate'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '--file',
        required=True,
        help='Path to copy-deliverable.md'
    )
    
    parser.add_argument(
        '--feature-name',
        required=True,
        help='Feature name (used for output directory)'
    )
    
    parser.add_argument(
        '--category',
        default='Lab',
        help='Content category (default: Lab)'
    )
    
    args = parser.parse_args()
    
    if args.command == 'generate':
        generator = LocalHTMLGenerator()
        output_dir, html_path = generator.generate(
            args.file,
            args.feature_name,
            args.category
        )
        
        print(f"\n📦 Files saved to: {output_dir}")
        print(f"🌐 Open in browser: {html_path}")


if __name__ == '__main__':
    main()
