import os
import json
import csv
from pathlib import Path
from datetime import datetime

# Imports pour PDF
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class FileCreatorAgent:
    def __init__(self, output_folder="exports"):
        self.output_folder = output_folder
        Path(output_folder).mkdir(exist_ok=True)
        print(f"📁 FileCreator - Dossier: {output_folder}")
        
        self.supported_formats = {
            '.txt': self.create_txt,
            '.csv': self.create_csv,
            '.json': self.create_json,
            '.md': self.create_markdown,
            '.html': self.create_html,
            '.py': self.create_python,
            '.xml': self.create_xml,
            '.pdf': self.create_pdf
        }
    
    def create_file(self, content, filename, format_type='txt', subfolder=None):
        try:
            # Ajouter l'extension si nécessaire
            if not any(filename.endswith(ext) for ext in self.supported_formats.keys()):
                filename = f"{filename}.{format_type}"

            ext = Path(filename).suffix.lower()

            if ext in self.supported_formats:
                # Construire le chemin avec ou sans sous-dossier
                if subfolder:
                    # Nettoyer le nom du sous-dossier
                    subfolder = subfolder.strip('/\\')
                    file_path = os.path.join(self.output_folder, subfolder, filename)
                else:
                    file_path = os.path.join(self.output_folder, filename)

                # Créer automatiquement les dossiers parents (incluant les sous-dossiers)
                Path(file_path).parent.mkdir(parents=True, exist_ok=True)

                # Appeler la fonction de création du fichier
                self.supported_formats[ext](file_path, content)

                return {
                    'success': True,
                    'file_path': file_path,
                    'filename': filename,
                    'subfolder': subfolder
                }

            return {
                'success': False,
                'error': f"Format non supporté: {ext}",
                'supported': list(self.supported_formats.keys())
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def create_txt(self, file_path, content):
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def create_csv(self, file_path, content):
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            if isinstance(content, list):
                writer = csv.writer(f)
                for row in content:
                    writer.writerow(row)
            elif isinstance(content, dict):
                writer = csv.DictWriter(f, fieldnames=content.keys())
                writer.writeheader()
                writer.writerow(content)
            else:
                f.write(str(content))
    
    def create_json(self, file_path, content):
        with open(file_path, 'w', encoding='utf-8') as f:
            if isinstance(content, (dict, list)):
                json.dump(content, f, indent=2, ensure_ascii=False)
            else:
                json.dump({'data': content}, f, indent=2, ensure_ascii=False)
    
    def create_markdown(self, file_path, content):
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def create_html(self, file_path, content):
        with open(file_path, 'w', encoding='utf-8') as f:
            if not content.strip().startswith('<!DOCTYPE'):
                content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document généré</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #667eea; }}
        .content {{ background: #f8f9fa; padding: 20px; border-radius: 8px; }}
    </style>
</head>
<body>
    <h1>📄 Document généré</h1>
    <div class="content">
        {content}
    </div>
    <footer style="margin-top: 40px; color: #888; font-size: 0.9rem;">
        Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}
    </footer>
</body>
</html>"""
            f.write(content)
    
    def create_python(self, file_path, content):
        with open(file_path, 'w', encoding='utf-8') as f:
            if not content.strip().startswith('#') and 'def ' not in content:
                content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fichier généré automatiquement
Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}
"""

{content}

if __name__ == "__main__":
    print("✅ Fichier exécuté avec succès")
'''
            f.write(content)
    
    def create_xml(self, file_path, content):
        with open(file_path, 'w', encoding='utf-8') as f:
            if not content.strip().startswith('<?xml'):
                content = f'''<?xml version="1.0" encoding="UTF-8"?>
<document>
    <generated_at>{datetime.now().isoformat()}</generated_at>
    <content>{content}</content>
</document>'''
            f.write(content)
    
    def create_pdf(self, file_path, content):
        """Crée un fichier PDF valide avec le contenu"""
        try:
            doc = SimpleDocTemplate(
                file_path,
                pagesize=A4,
                topMargin=2*cm,
                bottomMargin=2*cm,
                leftMargin=2*cm,
                rightMargin=2*cm
            )
            
            styles = getSampleStyleSheet()
            story = []
            
            # Titre
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                textColor=colors.HexColor('#667eea'),
                spaceAfter=12
            )
            story.append(Paragraph("📄 Document généré", title_style))
            story.append(Spacer(1, 12))
            
            # Date
            date_style = ParagraphStyle(
                'DateStyle',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.grey,
                spaceAfter=20
            )
            story.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", date_style))
            story.append(Spacer(1, 10))
            
            # Contenu
            content_style = ParagraphStyle(
                'ContentStyle',
                parent=styles['Normal'],
                fontSize=11,
                leading=16,
                spaceAfter=6
            )
            
            # Analyser le contenu
            lines = content.strip().split('\n')
            has_table = len(lines) > 1 and ',' in lines[0] and all(',' in line for line in lines if line.strip())
            
            if has_table:
                # Créer un tableau
                data = []
                for line in lines:
                    if line.strip():
                        row = [cell.strip() for cell in line.split(',')]
                        data.append(row)
                
                if data:
                    # Style du tableau
                    table_style = TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                        ('FONTSIZE', (0, 1), (-1, -1), 9),
                        ('TOPPADDING', (0, 1), (-1, -1), 4),
                        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
                    ])
                    
                    table = Table(data)
                    table.setStyle(table_style)
                    story.append(table)
            else:
                # Texte normal
                for line in lines:
                    if line.strip():
                        story.append(Paragraph(line, content_style))
            
            # Footer
            story.append(Spacer(1, 30))
            footer_style = ParagraphStyle(
                'FooterStyle',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.grey,
                alignment=1
            )
            story.append(Paragraph("---", footer_style))
            story.append(Spacer(1, 6))
            story.append(Paragraph("Document généré automatiquement par FileCreator Agent", footer_style))
            
            doc.build(story)
            print(f"✅ PDF créé: {file_path}")
            
        except Exception as e:
            print(f"❌ Erreur création PDF: {e}")
            # Fallback: PDF simple
            try:
                c = canvas.Canvas(file_path, pagesize=A4)
                width, height = A4
                
                c.setFont("Helvetica-Bold", 16)
                c.drawString(2*cm, height - 2*cm, "📄 Document généré")
                
                c.setFont("Helvetica", 10)
                c.drawString(2*cm, height - 3*cm, f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}")
                
                c.setFont("Helvetica", 11)
                y = height - 4.5*cm
                for line in content.split('\n'):
                    if y < 2*cm:
                        c.showPage()
                        y = height - 2*cm
                        c.setFont("Helvetica", 11)
                    if line.strip():
                        # Tronquer les lignes trop longues
                        if len(line) > 80:
                            line = line[:77] + "..."
                        c.drawString(2*cm, y, line)
                    y -= 0.6*cm
                
                c.save()
                print(f"✅ PDF (fallback) créé: {file_path}")
            except Exception as e2:
                print(f"❌ Erreur fallback PDF: {e2}")
                raise

    def create_folder(self, folder_name):
        """Crée un dossier dans le répertoire de sortie"""
        folder_path = os.path.join(self.output_folder, folder_name)
        Path(folder_path).mkdir(parents=True, exist_ok=True)
        return {
            'success': True,
            'folder_path': folder_path,
            'folder_name': folder_name
        }

    def create_subfolder(self, parent_folder, subfolder_name):
        """Crée un sous-dossier dans un dossier existant"""
        folder_path = os.path.join(self.output_folder, parent_folder, subfolder_name)
        Path(folder_path).mkdir(parents=True, exist_ok=True)
        return {
            'success': True,
            'folder_path': folder_path,
            'parent_folder': parent_folder,
            'subfolder_name': subfolder_name
        }

    def list_files(self, subfolder=None):
        """Liste les fichiers dans le dossier ou sous-dossier spécifié"""
        if subfolder:
            folder_path = os.path.join(self.output_folder, subfolder)
            if not os.path.exists(folder_path):
                return {'success': False, 'error': f'Dossier {subfolder} non trouvé'}
        else:
            folder_path = self.output_folder
            
        files = os.listdir(folder_path)
        return {
            'success': True,
            'files': [{
                'name': f,
                'size': os.path.getsize(os.path.join(folder_path, f)),
                'modified': datetime.fromtimestamp(os.path.getmtime(os.path.join(folder_path, f))).strftime('%d/%m/%Y %H:%M'),
                'is_folder': os.path.isdir(os.path.join(folder_path, f))
            } for f in files]
        }

    def delete_file(self, filename, subfolder=None):
        """Supprime un fichier dans le dossier ou sous-dossier spécifié"""
        if subfolder:
            file_path = os.path.join(self.output_folder, subfolder, filename)
        else:
            file_path = os.path.join(self.output_folder, filename)
            
        if os.path.exists(file_path):
            os.remove(file_path)
            return {'success': True, 'message': f'Fichier {filename} supprimé'}
        return {'success': False, 'error': 'Fichier non trouvé'}

    def delete_folder(self, folder_name):
        """Supprime un dossier (doit être vide)"""
        folder_path = os.path.join(self.output_folder, folder_name)
        if os.path.exists(folder_path):
            try:
                os.rmdir(folder_path)
                return {'success': True, 'message': f'Dossier {folder_name} supprimé'}
            except OSError:
                return {'success': False, 'error': 'Le dossier n\'est pas vide'}
        return {'success': False, 'error': 'Dossier non trouvé'}