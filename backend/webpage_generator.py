"""
Webpage Generator Service
Converts privacy policy analysis into embeddable HTML webpages
"""

import uuid
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template

from .models import PrivacyPolicyDocument, ProcessedSection


class WebpageTemplate:
    """Template configuration for generated webpages"""
    
    def __init__(self, name: str, description: str, template_file: str, 
                 css_file: str, features: List[str]):
        self.name = name
        self.description = description
        self.template_file = template_file
        self.css_file = css_file
        self.features = features


class WebpageGenerator:
    """Service for generating embeddable privacy policy webpages"""
    
    def __init__(self, output_dir: str = "generated_webpages"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize templates directory
        self.templates_dir = Path("backend/templates/webpages")
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=True
        )
        
        # Available templates
        self.templates = {
            "modern": WebpageTemplate(
                name="Modern Interactive",
                description="Clean, modern design with interactive elements and animations",
                template_file="modern.html",
                css_file="modern.css",
                features=["interactive_sections", "animations", "responsive", "dark_mode"]
            ),
            "classic": WebpageTemplate(
                name="Classic Professional",
                description="Traditional, professional layout suitable for corporate websites",
                template_file="classic.html", 
                css_file="classic.css",
                features=["professional", "print_friendly", "accessibility"]
            ),
            "minimal": WebpageTemplate(
                name="Minimal Clean",
                description="Simple, distraction-free design focusing on content",
                template_file="minimal.html",
                css_file="minimal.css", 
                features=["lightweight", "fast_loading", "mobile_first"]
            ),
            "interactive": WebpageTemplate(
                name="Fully Interactive",
                description="Rich interactive experience with quizzes and dynamic content",
                template_file="interactive.html",
                css_file="interactive.css",
                features=["quizzes", "tooltips", "progress_tracking", "gamification"]
            )
        }
        
        # Create template files if they don't exist
        self._create_default_templates()
    
    def _create_default_templates(self):
        """Create default template files if they don't exist"""
        for template_id, template in self.templates.items():
            template_path = self.templates_dir / template.template_file
            css_path = self.templates_dir / template.css_file
            
            if not template_path.exists():
                self._create_template_file(template_path, template_id)
            
            if not css_path.exists():
                self._create_css_file(css_path, template_id)
    
    def generate_webpage(self, 
                        document: PrivacyPolicyDocument,
                        sections: List[ProcessedSection],
                        template_id: str = "modern",
                        custom_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate an embeddable webpage from policy analysis results
        
        Args:
            document: Processed privacy policy document
            sections: Processed policy sections
            template_id: Template to use for generation
            custom_options: Custom styling and content options
            
        Returns:
            Dictionary with webpage info including URLs and metadata
        """
        
        if template_id not in self.templates:
            raise ValueError(f"Template '{template_id}' not found. Available: {list(self.templates.keys())}")
        
        template = self.templates[template_id]
        options = custom_options or {}
        
        # Generate unique webpage ID
        webpage_id = str(uuid.uuid4())
        
        # Prepare template data
        template_data = self._prepare_template_data(document, sections, options)
        
        # Generate HTML content
        html_content = self._render_template(template.template_file, template_data)
        
        # Generate CSS content
        css_content = self._render_css(template.css_file, template_data)
        
        # Create webpage directory
        webpage_dir = self.output_dir / webpage_id
        webpage_dir.mkdir(exist_ok=True)
        
        # Write files
        html_file = webpage_dir / "index.html"
        css_file = webpage_dir / "styles.css"
        metadata_file = webpage_dir / "metadata.json"
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        with open(css_file, 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        # Create metadata
        metadata = {
            "webpage_id": webpage_id,
            "template_id": template_id,
            "company_name": document.company_name,
            "title": document.title,
            "created_at": datetime.now().isoformat(),
            "processing_id": document.id,
            "options": options,
            "stats": {
                "total_sections": len(sections),
                "high_risk_sections": document.high_risk_sections,
                "interactive_sections": document.interactive_sections,
                "overall_risk": document.overall_risk_level.value,
                "user_friendliness": document.user_friendliness_score
            },
            "urls": {
                "standalone": f"/webpage/{webpage_id}",
                "embed_iframe": f"/embed/iframe/{webpage_id}",
                "embed_widget": f"/embed/widget/{webpage_id}",
                "api": f"/api/webpage/{webpage_id}"
            }
        }
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        return metadata
    
    def _prepare_template_data(self, document: PrivacyPolicyDocument, 
                             sections: List[ProcessedSection],
                             options: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for template rendering"""
        
        # Sort sections by priority
        sorted_sections = sorted(sections, key=lambda s: s.section_priority)
        
        # Group sections by component type
        section_groups = {}
        for section in sorted_sections:
            comp_type = section.component_type
            if comp_type not in section_groups:
                section_groups[comp_type] = []
            section_groups[comp_type].append(section)
        
        # Calculate additional stats
        total_words = sum(section.word_count for section in sorted_sections)
        quiz_sections = [section for section in sorted_sections if section.quiz]
        high_sensitivity_sections = [section for section in sorted_sections 
                                   if section.user_impact.sensitivity_score >= 8.0]
        
        return {
            "document": document,
            "sections": sorted_sections,
            "section_groups": section_groups,
            "company_name": document.company_name,
            "policy_title": document.title,
            "created_date": datetime.now().strftime("%B %d, %Y"),
            "stats": {
                "total_sections": len(sorted_sections),
                "total_words": total_words,
                "reading_time": max(1, total_words // 200),
                "high_risk_count": len(high_sensitivity_sections),
                "quiz_count": len(quiz_sections),
                "overall_risk": document.overall_risk_level.value,
                "sensitivity_score": document.overall_sensitivity_score,
                "privacy_impact": document.overall_privacy_impact,
                "user_friendliness": document.user_friendliness_score,
                "compliance_score": document.compliance_score
            },
            "options": {
                "show_quizzes": options.get("show_quizzes", True),
                "show_risk_indicators": options.get("show_risk_indicators", True),
                "enable_dark_mode": options.get("enable_dark_mode", False),
                "compact_layout": options.get("compact_layout", False),
                "custom_colors": options.get("custom_colors", {}),
                "company_logo": options.get("company_logo"),
                "footer_text": options.get("footer_text"),
                "contact_info": options.get("contact_info", {})
            }
        }
    
    def _render_template(self, template_file: str, data: Dict[str, Any]) -> str:
        """Render HTML template with data"""
        try:
            template = self.jinja_env.get_template(template_file)
            return template.render(**data)
        except Exception as e:
            # Fallback to basic template
            return self._create_basic_html(data)
    
    def _render_css(self, css_file: str, data: Dict[str, Any]) -> str:
        """Render CSS template with data"""
        try:
            template = self.jinja_env.get_template(css_file)
            return template.render(**data)
        except Exception as e:
            # Fallback to basic CSS
            return self._create_basic_css(data)
    
    def _create_basic_html(self, data: Dict[str, Any]) -> str:
        """Create basic HTML fallback"""
        company_name = data.get("company_name", "Company")
        sections = data.get("sections", [])
        stats = data.get("stats", {})
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{company_name} Privacy Policy</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>{company_name} Privacy Policy</h1>
            <div class="stats">
                <span class="stat">Risk Level: {stats.get('overall_risk', 'Unknown').title()}</span>
                <span class="stat">Reading Time: {stats.get('reading_time', 0)} min</span>
                <span class="stat">User Friendliness: {stats.get('user_friendliness', 0)}/5</span>
            </div>
        </header>
        
        <main class="content">"""
        
        for section in sections:
            html += f"""
            <section class="policy-section risk-{section.user_impact.risk_level.value}">
                <h2>{section.title}</h2>
                <div class="summary">{section.summary}</div>
                
                <div class="metrics">
                    <span class="metric">Sensitivity: {section.user_impact.sensitivity_score:.1f}/10</span>
                    <span class="metric">Privacy Impact: {section.user_impact.privacy_impact_score:.1f}/10</span>
                    <span class="metric">User Control: {section.user_impact.user_control}/5</span>
                </div>
                
                {self._render_key_concerns(section.user_impact.key_concerns)}
                {self._render_user_rights([right.value for right in section.user_rights])}
                {self._render_data_types([dt.value for dt in section.data_types])}
            </section>"""
        
        html += """
        </main>
        
        <footer class="footer">
            <p>Generated by Dynamic Privacy Policy System</p>
            <p>Last updated: """ + data.get("created_date", "") + """</p>
        </footer>
    </div>
</body>
</html>"""
        
        return html
    
    def _render_key_concerns(self, concerns: List[str]) -> str:
        """Render key concerns section"""
        if not concerns:
            return ""
        
        html = '<div class="key-concerns"><h3>🚨 Key Concerns</h3><ul>'
        for concern in concerns:
            html += f'<li>{concern}</li>'
        html += '</ul></div>'
        return html
    
    def _render_user_rights(self, rights: List[str]) -> str:
        """Render user rights section"""
        if not rights:
            return ""
        
        html = '<div class="user-rights"><h3>✅ Your Rights</h3><ul>'
        for right in rights:
            html += f'<li>{right}</li>'
        html += '</ul></div>'
        return html
    
    def _render_data_types(self, data_types: List[str]) -> str:
        """Render data types section"""
        if not data_types:
            return ""
        
        html = '<div class="data-types"><h3>📊 Data Collected</h3><div class="tags">'
        for data_type in data_types:
            html += f'<span class="tag">{data_type}</span>'
        html += '</div></div>'
        return html
    
    def _create_basic_css(self, data: Dict[str, Any]) -> str:
        """Create basic CSS fallback"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: white;
            min-height: 100vh;
        }
        
        .header {
            text-align: center;
            padding: 40px 0;
            border-bottom: 2px solid #e0e0e0;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 20px;
            color: #2c3e50;
        }
        
        .stats {
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
        }
        
        .stat {
            background: #3498db;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 500;
        }
        
        .content {
            padding: 40px 0;
        }
        
        .policy-section {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .policy-section.risk-high {
            border-left: 4px solid #e74c3c;
        }
        
        .policy-section.risk-medium {
            border-left: 4px solid #f39c12;
        }
        
        .policy-section.risk-low {
            border-left: 4px solid #27ae60;
        }
        
        .policy-section h2 {
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.5em;
        }
        
        .summary {
            margin-bottom: 20px;
            font-size: 1.1em;
            line-height: 1.7;
        }
        
        .metrics {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .metric {
            background: #ecf0f1;
            padding: 6px 12px;
            border-radius: 15px;
            font-size: 0.85em;
            font-weight: 500;
        }
        
        .key-concerns {
            background: #fdf2f2;
            border: 1px solid #fadbd8;
            border-radius: 6px;
            padding: 15px;
            margin: 15px 0;
        }
        
        .key-concerns h3 {
            color: #c0392b;
            margin-bottom: 10px;
            font-size: 1.1em;
        }
        
        .user-rights {
            background: #f0f9f0;
            border: 1px solid #d5e7d5;
            border-radius: 6px;
            padding: 15px;
            margin: 15px 0;
        }
        
        .user-rights h3 {
            color: #27ae60;
            margin-bottom: 10px;
            font-size: 1.1em;
        }
        
        .data-types {
            background: #f0f7ff;
            border: 1px solid #cce7ff;
            border-radius: 6px;
            padding: 15px;
            margin: 15px 0;
        }
        
        .data-types h3 {
            color: #3498db;
            margin-bottom: 10px;
            font-size: 1.1em;
        }
        
        .tags {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
        
        .tag {
            background: #3498db;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.8em;
        }
        
        .footer {
            text-align: center;
            padding: 30px 0;
            border-top: 1px solid #e0e0e0;
            color: #7f8c8d;
            font-size: 0.9em;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .stats {
                gap: 10px;
            }
            
            .policy-section {
                padding: 20px;
            }
            
            .metrics {
                gap: 8px;
            }
        }
        """
    
    def _create_template_file(self, template_path: Path, template_id: str):
        """Create a template file (placeholder for now)"""
        # For now, we'll use the basic HTML structure
        # Later this can be expanded with more sophisticated templates
        template_path.write_text("""<!-- Template placeholder for {{ template_id }} -->
<!-- This will be replaced with actual Jinja2 templates -->
""")
    
    def _create_css_file(self, css_path: Path, template_id: str):
        """Create a CSS file (placeholder for now)"""
        # For now, we'll use the basic CSS
        # Later this can be expanded with template-specific styles
        css_path.write_text(f"""/* CSS template for {template_id} */
/* This will be replaced with actual template-specific CSS */
""")
    
    def get_available_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get information about available templates"""
        return {
            template_id: {
                "name": template.name,
                "description": template.description,
                "features": template.features
            }
            for template_id, template in self.templates.items()
        }
    
    def get_webpage_info(self, webpage_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a generated webpage"""
        webpage_dir = self.output_dir / webpage_id
        metadata_file = webpage_dir / "metadata.json"
        
        if not metadata_file.exists():
            return None
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def list_generated_webpages(self) -> List[Dict[str, Any]]:
        """List all generated webpages"""
        webpages = []
        
        for webpage_dir in self.output_dir.iterdir():
            if webpage_dir.is_dir():
                metadata_file = webpage_dir / "metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                            webpages.append(metadata)
                    except Exception:
                        continue
        
        return sorted(webpages, key=lambda x: x.get('created_at', ''), reverse=True) 