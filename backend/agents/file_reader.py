import os
import json
import csv
from pathlib import Path
from typing import List, Dict, Union

class FileReaderAgent:
    def __init__(self, upload_folder="uploads"):
        self.upload_folder = upload_folder
        Path(upload_folder).mkdir(exist_ok=True)
        print(f"📁 FileReader - Dossier: {upload_folder}")
    
    def read_file(self, file_path):
        try:
            ext = Path(file_path).suffix.lower()
            
            if ext == '.txt':
                return self.read_txt(file_path)
            elif ext == '.csv':
                return self.read_csv(file_path)
            elif ext == '.json':
                return self.read_json(file_path)
            else:
                return f"⚠️ Format non supporté: {ext}"
        except Exception as e:
            return f"❌ Erreur: {str(e)}"
    
    def read_txt(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return f"📄 {os.path.basename(file_path)}\n\n{content}"
    
    def read_csv(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        preview = ""
        for i, row in enumerate(rows[:10]):
            preview += f"  Ligne {i+1}: {', '.join(row)}\n"
        
        return f"""📊 CSV: {os.path.basename(file_path)}
📏 {len(rows)} lignes, {len(rows[0]) if rows else 0} colonnes

📋 Aperçu:
{preview}"""
    
    def read_json(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return f"📄 JSON: {os.path.basename(file_path)}\n\n{json.dumps(data, indent=2, ensure_ascii=False)[:1000]}"
        
        


class MiltiFileReaderAgent:
    def __init__(self, upload_folder="uploads", max_files=20, max_size_mb=50):
        self.upload_folder = upload_folder
        self.max_files = max_files  # Nombre max de fichiers à lire
        self.max_size_mb = max_size_mb  # Taille max par fichier (Mo)
        Path(upload_folder).mkdir(exist_ok=True)
        print(f"📁 FileReader - Dossier: {upload_folder}")
        print(f"📋 Max fichiers: {max_files} | Max taille: {max_size_mb} Mo")
    
    # ============================================
    # LIRE UN SEUL FICHIER
    # ============================================
    def read_file(self, file_path: str) -> str:
        """Lit un seul fichier"""
        try:
            # Vérifier la taille
            if not self._check_size(file_path):
                return f"⚠️ Fichier trop gros: {os.path.basename(file_path)}"

            ext = Path(file_path).suffix.lower()
            
            if ext == '.txt':
                return self.read_txt(file_path)
            elif ext == '.csv':
                return self.read_csv(file_path)
            elif ext == '.json':
                return self.read_json(file_path)
            elif ext in ['.pdf']:
                return self.read_pdf(file_path)
            elif ext in ['.docx', '.doc']:
                return self.read_docx(file_path)
            elif ext in ['.xlsx', '.xls']:
                return self.read_excel(file_path)
            else:
                return f"⚠️ Format non supporté: {ext}"
        except Exception as e:
            return f"❌ Erreur: {str(e)}"
    
    # ============================================
    # LIRE PLUSIEURS FICHIERS
    # ============================================
    def read_files(self, file_paths: Union[str, List[str]], combine: bool = True) -> Dict[str, Union[str, Dict]]:
        """
        Lit plusieurs fichiers
        
        Args:
            file_paths: Chemin d'un fichier ou liste de chemins
            combine: Si True, fusionne les résultats en un seul texte
                     Si False, retourne un dictionnaire par fichier
        
        Returns:
            Dictionnaire avec les résultats ou texte combiné
        """
        # Si un seul fichier est passé en string, le convertir en liste
        if isinstance(file_paths, str):
            file_paths = [file_paths]
        
        # Vérifier le nombre de fichiers
        if len(file_paths) > self.max_files:
            return {
                'error': f"❌ Trop de fichiers (max {self.max_files})",
                'count': len(file_paths)
            }
        
        results = {}
        errors = []
        total_size = 0

        for i, path in enumerate(file_paths):
            if not os.path.exists(path):
                errors.append(f"⚠️ Fichier {i+1} introuvable: {path}")
                continue

            # Vérifier la taille
            size_mb = os.path.getsize(path) / (1024 * 1024)
            total_size += size_mb

            if size_mb > self.max_size_mb:
                errors.append(f"⚠️ Fichier {i+1} trop gros: {os.path.basename(path)} ({size_mb:.1f} Mo > {self.max_size_mb} Mo)")
                continue

            # Lire le fichier
            content = self.read_file(path)
            filename = os.path.basename(path)
            results[filename] = content

        # Vérifier la taille totale
        if total_size > self.max_size_mb * 2:
            errors.append(f"⚠️ Taille totale trop grande: {total_size:.1f} Mo")

        # Retourner les résultats
        if combine:
            return self._combine_results(results, errors)
        else:
            return {
                'results': results,
                'errors': errors,
                'count': len(results),
                'total_size_mb': round(total_size, 2)
            }
    
    # ============================================
    # COMBINER LES RÉSULTATS
    # ============================================
    def _combine_results(self, results: Dict, errors: List) -> str:
        """Combine les résultats en un seul texte"""
        if not results and not errors:
            return "📭 Aucun fichier à lire"

        output = []
        output.append(f"📊 RÉSULTAT DE LECTURE ({len(results)} fichiers)")
        output.append("=" * 50)

        for filename, content in results.items():
            output.append(f"\n📄 {filename}")
            output.append("-" * 30)
            output.append(content)

        if errors:
            output.append("\n⚠️ ERREURS:")
            for err in errors:
                output.append(f"  {err}")

        return "\n".join(output)

    # ============================================
    # LIRE UN DOSSIER ENTIER
    # ============================================
    def read_folder(self, folder_path: str, extensions: List[str] = None) -> str:
        """
        Lit tous les fichiers d'un dossier
        
        Args:
            folder_path: Chemin du dossier
            extensions: Liste des extensions à inclure (ex: ['.txt', '.pdf'])
                        Si None, lit tous les fichiers
        """
        if not os.path.exists(folder_path):
            return f"❌ Dossier introuvable: {folder_path}"

        files = []
        for root, dirs, filenames in os.walk(folder_path):
            for filename in filenames:
                ext = Path(filename).suffix.lower()
                if extensions is None or ext in extensions:
                    files.append(os.path.join(root, filename))

        if not files:
            return f"📭 Aucun fichier trouvé dans {folder_path}"

        return self.read_files(files)

    # ============================================
    # VÉRIFIER LA TAILLE DU FICHIER
    # ============================================
    def _check_size(self, file_path: str) -> bool:
        """Vérifie si le fichier ne dépasse pas la taille max"""
        try:
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            return size_mb <= self.max_size_mb
        except:
            return False

    # ============================================
    # MÉTHODES DE LECTURE PAR FORMAT
    # ============================================
    
    def read_txt(self, file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return f"📄 {os.path.basename(file_path)}\n\n{content[:5000]}" + ("..." if len(content) > 5000 else "")

    def read_csv(self, file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        preview = ""
        for i, row in enumerate(rows[:10]):
            preview += f"  Ligne {i+1}: {', '.join(row)}\n"
        
        return f"""📊 CSV: {os.path.basename(file_path)}
📏 {len(rows)} lignes, {len(rows[0]) if rows else 0} colonnes

📋 Aperçu (10 premières lignes):
{preview}"""

    def read_json(self, file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Limiter l'affichage
        content = json.dumps(data, indent=2, ensure_ascii=False)
        if len(content) > 3000:
            content = content[:3000] + "\n... (tronqué)"
        
        return f"📄 JSON: {os.path.basename(file_path)}\n\n{content}"

    def read_pdf(self, file_path: str) -> str:
        """Lecture de PDF (nécessite PyPDF2 ou pypdf)"""
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(file_path)
            num_pages = len(reader.pages)
            
            content = ""
            for i, page in enumerate(reader.pages[:5]):  # Limiter à 5 pages
                content += page.extract_text()
            
            return f"""📄 PDF: {os.path.basename(file_path)}
📏 {num_pages} pages

📋 Contenu (5 premières pages):
{content[:3000]}...""" if len(content) > 3000 else content
        except ImportError:
            return "⚠️ PyPDF2 non installé. Installez-le avec: pip install pypdf"
        except Exception as e:
            return f"❌ Erreur PDF: {str(e)}"

    def read_docx(self, file_path: str) -> str:
        """Lecture de DOCX (nécessite python-docx)"""
        try:
            from docx import Document
            doc = Document(file_path)
            content = "\n".join([p.text for p in doc.paragraphs])
            return f"📄 DOCX: {os.path.basename(file_path)}\n\n{content[:5000]}" + ("..." if len(content) > 5000 else "")
        except ImportError:
            return "⚠️ python-docx non installé. Installez-le avec: pip install python-docx"
        except Exception as e:
            return f"❌ Erreur DOCX: {str(e)}"

    def read_excel(self, file_path: str) -> str:
        """Lecture de Excel (nécessaire openpyxl)"""
        try:
            from openpyxl import load_workbook
            wb = load_workbook(file_path, data_only=True)
            sheet = wb.active
            
            content = f"📊 Excel: {os.path.basename(file_path)}\n"
            content += f"📏 {sheet.max_row} lignes, {sheet.max_column} colonnes\n\n"
            
            for i, row in enumerate(sheet.iter_rows(values_only=True), 1):
                if i > 20:
                    content += f"... ({sheet.max_row - 20} lignes supplémentaires)\n"
                    break
                content += f"  Ligne {i}: {', '.join([str(cell) if cell is not None else '' for cell in row])}\n"
            
            return content
        except ImportError:
            return "⚠️ openpyxl non installé. Installez-le avec: pip install openpyxl"
        except Exception as e:
            return f"❌ Erreur Excel: {str(e)}"       
        
 