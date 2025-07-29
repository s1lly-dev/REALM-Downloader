# ================================================================================================================================================================
# Author  : VergePoland (OG Dev), T (New Developer), Cheato (Liberator Dev), Lungu (Shears Dev), SlejmUr (SlejmUr's Downloader), Puppetino (FAQs) Philo (Biography)
# ================================================================================================================================================================

import threading
import json
import os
import subprocess
import urllib.request
import zipfile
import shutil
from functools import partial
from pathlib import Path
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.switch import Switch
from kivy.uix.slider import Slider
from kivy.uix.scrollview import ScrollView
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle, Line, RoundedRectangle
from kivy.uix.widget import Widget
from kivy.uix.image import Image
import downloader # type: ignore

COLORS = {
    'background': (0.04, 0.04, 0.04, 1),      
    'surface': (0.08, 0.08, 0.08, 1),        
    'surface_variant': (0.12, 0.12, 0.12, 1), 
    'primary': (0.13, 0.59, 0.95, 1),      
    'primary_variant': (0.10, 0.47, 0.76, 1), 
    'secondary': (0.25, 0.25, 0.25, 1),       
    'accent': (0.0, 0.8, 0.4, 1),           
    'warning': (1.0, 0.6, 0.0, 1),          
    'error': (0.9, 0.2, 0.2, 1),        
    'text_primary': (0.95, 0.95, 0.95, 1),    
    'text_secondary': (0.7, 0.7, 0.7, 1), 
    'text_disabled': (0.5, 0.5, 0.5, 1),  
    'border': (0.2, 0.2, 0.2, 1),          
    'hover': (0.15, 0.15, 0.15, 1),       
}

Window.clearcolor = COLORS['background']
Window.size = (1400, 900)
Window.minimum_width = 1200
Window.minimum_height = 800

class UserSettings:
    """Enhanced settings management with file persistence"""
    _settings_file = Path("settings.json")
    
    def __init__(self):
        self.username = ""
        self.password = ""
        self.remember_password = True
        self.max_downloads = 25
        self.auto_start_downloads = False
        self.downloads_folder = str(Path.cwd() / "Downloads")
        self.resources_folder = str(Path.cwd() / "Resources")
        self.theme = "dark"
        self.game_username = "ThrowbackUser"
        self.auto_configure = True
        self.show_patch_notes = True
        self.auto_download_resources = True
        self.check_resources_on_startup = True
        self.load_settings()
    
    def load_settings(self):
        """Load settings from file"""
        if self._settings_file.exists():
            try:
                with open(self._settings_file, 'r') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if hasattr(self, key):
                            setattr(self, key, value)
            except Exception as e:
                print(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save settings to file"""
        try:
            data = {
                'username': self.username,
                'password': self.password if self.remember_password else '',
                'remember_password': self.remember_password,
                'max_downloads': self.max_downloads,
                'auto_start_downloads': self.auto_start_downloads,
                'downloads_folder': self.downloads_folder,
                'resources_folder': self.resources_folder,
                'theme': self.theme,
                'game_username': self.game_username,
                'auto_configure': self.auto_configure,
                'show_patch_notes': self.show_patch_notes,
                'auto_download_resources': self.auto_download_resources,
                'check_resources_on_startup': self.check_resources_on_startup
            }
            with open(self._settings_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")

user_settings = UserSettings()

def patched_ask_credentials():
    if user_settings.password and user_settings.remember_password:
        return (user_settings.username, user_settings.password)
    else:
        return (user_settings.username, "--remember-password")

downloader.ask_credentials = patched_ask_credentials

if hasattr(downloader, 'DOWNLOADS_DIR'):
    downloader.DOWNLOADS_DIR = Path(user_settings.downloads_folder)

class ResourceManager:
    """Manage resource downloads and setup"""
    
    @staticmethod
    def ensure_directories():
        """Ensure all necessary directories exist"""
        try:
            resources_path = Path(user_settings.resources_folder)
            tools_path = resources_path / "Tools"
            
            resources_path.mkdir(exist_ok=True)
            tools_path.mkdir(exist_ok=True)
            
            return True, "Directories created successfully"
        except Exception as e:
            return False, f"Failed to create directories: {str(e)}"
    
    @staticmethod
    def download_7zip():
        """Download 7zip executable"""
        try:
            resources_path = Path(user_settings.resources_folder)
            seven_zip_path = resources_path / "7z.exe"
            
            if seven_zip_path.exists():
                return True, "7zip already exists"
            
            url = "https://www.7-zip.org/a/7zr.exe"
            
            print(f"Downloading 7zip to {seven_zip_path}")
            urllib.request.urlretrieve(url, seven_zip_path)
            
            if seven_zip_path.exists() and seven_zip_path.stat().st_size > 0:
                return True, f"7zip downloaded successfully to {seven_zip_path}"
            else:
                return False, "7zip download failed - file is empty or missing"
                
        except Exception as e:
            return False, f"Failed to download 7zip: {str(e)}"
    
    @staticmethod
    def check_resources():
        """Check if all required resources are available"""
        resources_path = Path(user_settings.resources_folder)
        seven_zip_path = resources_path / "7z.exe"
        
        missing_resources = []
        
        if not resources_path.exists():
            missing_resources.append("Resources directory")
        
        if not seven_zip_path.exists():
            missing_resources.append("7zip executable")
        
        return len(missing_resources) == 0, missing_resources
    
    @staticmethod
    def setup_all_resources():
        """Setup all required resources"""
        try:
            success, message = ResourceManager.ensure_directories()
            if not success:
                return False, message
            
            success, message = ResourceManager.download_7zip()
            if not success:
                return False, message
            
            return True, "All resources setup successfully"
            
        except Exception as e:
            return False, f"Failed to setup resources: {str(e)}"

class PatchManager:
    """Manage HeatedMetal patches"""
    
    @staticmethod
    def download_heated_metal():
        """Download HeatedMetal patches"""
        """CUM"""
        try:
            url = "https://github.com/DataCluster0/HeatedMetal/releases/download/0.2.3/HeatedMetal.7z"
            output_path = Path("HeatedMetal.7z")
            
            print(f"Downloading HeatedMetal from {url}")
            
            def download_with_progress(url, filepath):
                response = urllib.request.urlopen(url)
                total_size = int(response.headers.get('Content-Length', 0))
                
                with open(filepath, 'wb') as f:
                    downloaded = 0
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"Download progress: {progress:.1f}%")
            
            download_with_progress(url, output_path)
            
            if not output_path.exists() or output_path.stat().st_size == 0:
                return False, "Download failed - file is missing or empty"
            
            y5s3_path = Path(user_settings.downloads_folder) / "Y5S4_NeonDawnHM"
            if y5s3_path.exists():
                extract_path = y5s3_path
            else:
                extract_path = Path(user_settings.resources_folder) / "Tools" / "HeatedMetal"
                extract_path.mkdir(parents=True, exist_ok=True)
            
            print(f"Extracting to {extract_path}")
            
            seven_zip_path = Path(user_settings.resources_folder) / "7z.exe"
            if seven_zip_path.exists():
                try:
                    result = subprocess.run([
                        str(seven_zip_path), "x", "-y", 
                        f"-o{extract_path}", str(output_path), "-aoa"
                    ], capture_output=True, text=True, check=True)
                    print(f"7zip extraction result: {result.stdout}")
                except subprocess.CalledProcessError as e:
                    print(f"7zip extraction failed: {e.stderr}")
                    output_path.unlink()  
                    return False, f"Extraction failed: {e.stderr}"
            else:
                output_path.unlink() 
                return False, "7zip is required to extract HeatedMetal patches. Please setup resources first in Settings."
            
            output_path.unlink()
            
            if extract_path.exists() and any(extract_path.iterdir()):
                return True, f"HeatedMetal patches installed to {extract_path}"
            else:
                return False, "Extraction failed - no files were extracted"
            
        except Exception as e:
            print(f"HeatedMetal download error: {e}")
            return False, f"Failed to download HeatedMetal: {str(e)}"

class ToolManager:
    """Manage additional tools downloads"""
    
    @staticmethod
    def download_liberator():
        """Download R6 Liberator tool"""
        try:
            url = "https://github.com/SlejmUr/Manifest_Tool_TB/raw/main/R6_Liberator_0.0.0.22.exe"
            tools_path = Path(user_settings.resources_folder) / "Tools"
            tools_path.mkdir(parents=True, exist_ok=True)
            output_path = tools_path / "R6_Liberator_0.0.0.22.exe"
            
            print(f"Downloading R6 Liberator from {url}")
            urllib.request.urlretrieve(url, output_path)
            
            if output_path.exists() and output_path.stat().st_size > 0:
                return True, f"R6 Liberator downloaded to {output_path}"
            else:
                return False, "R6 Liberator download failed - file is missing or empty"
            
        except Exception as e:
            print(f"R6 Liberator download error: {e}")
            return False, f"Failed to download R6 Liberator: {str(e)}"
    
    @staticmethod
    def download_dxvk():
        """Download DXVK for Siege"""
        try:
            url = "https://github.com/Vergepoland/r6-downloader/raw/refs/heads/main/Siege-DXVK.zip"
            output_path = Path("Siege-DXVK.zip")
            
            print(f"Downloading Siege DXVK from {url}")
            urllib.request.urlretrieve(url, output_path)
            
            if not output_path.exists() or output_path.stat().st_size == 0:
                return False, "Download failed - file is missing or empty"
            
            extract_path = Path(user_settings.resources_folder) / "Tools" / "Siege-DXVK"
            extract_path.mkdir(parents=True, exist_ok=True)
            
            seven_zip_path = Path(user_settings.resources_folder) / "7z.exe"
            if seven_zip_path.exists():
                try:
                    subprocess.run([
                        str(seven_zip_path), "x", "-y", 
                        f"-o{extract_path}", str(output_path), "-aoa"
                    ], check=True, capture_output=True)
                except subprocess.CalledProcessError as e:
                    print(f"7zip extraction failed: {e}")
                    with zipfile.ZipFile(output_path, 'r') as zip_ref:
                        zip_ref.extractall(extract_path)
            else:
                with zipfile.ZipFile(output_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
            
            output_path.unlink()
            
            if extract_path.exists() and any(extract_path.iterdir()):
                return True, f"Siege DXVK installed to {extract_path}"
            else:
                return False, "Extraction failed - no files were extracted"
            
        except Exception as e:
            print(f"Siege DXVK download error: {e}")
            return False, f"Failed to download Siege DXVK: {str(e)}"

class ConfigEditor:
    """Handle CPlay.ini and CODEX.ini editing"""
    
    @staticmethod
    def find_config_files(install_path):
        """Find CPlay.ini and CODEX.ini files in installation directory"""
        config_files = []
        install_dir = Path(install_path)
        
        for config_name in ['CPlay.ini', 'CODEX.ini']:
            config_files.extend(install_dir.rglob(config_name))
        
        return config_files
    
    @staticmethod
    def read_config_file(file_path):
        """Read and parse config file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading config file {file_path}: {e}")
            return None
    
    @staticmethod
    def write_config_file(file_path, content):
        """Write config file with new content"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error writing config file {file_path}: {e}")
            return False
    
    @staticmethod
    def update_username_in_config(content, new_username):
        """Update username in config content"""
        lines = content.split('\n')
        updated_lines = []
        
        for line in lines:
            if line.strip().startswith('Username =') or line.strip().startswith('Username='):
                if '=' in line:
                    key_part = line.split('=')[0].strip()
                    updated_lines.append(f"{key_part} = {new_username}")
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)
        
        return '\n'.join(updated_lines)

class GameInfo:
    """Enhanced information about each R6 season/game with patch notes"""
    def __init__(self, name, folder_name, description, release_date, size_mb=0, patch_notes=None):
        self.name = name
        self.folder_name = folder_name
        self.description = description
        self.release_date = release_date
        self.size_mb = size_mb
        self.is_installed = False
        self.install_path = None
        self.download_progress = 0
        self.is_downloading = False
        self.patch_notes = patch_notes or []
        self.version = self._extract_version()
    
    def _extract_version(self):
        """Extract version from folder name"""
        if 'Y1S' in self.folder_name:
            parts = self.folder_name.split('_')
            if len(parts) >= 2:
                return parts[0] 
        elif 'TTS' in self.folder_name or 'Test' in self.name:
            return "TTS"
        return "Unknown"
    
    def check_installation(self, downloads_folder):
        """Check if this season is installed"""
        install_path = Path(downloads_folder) / self.folder_name
        self.is_installed = install_path.exists() and any(install_path.iterdir())
        self.install_path = str(install_path) if self.is_installed else None
        
        if self.is_installed:
            try:
                total_size = sum(f.stat().st_size for f in install_path.rglob('*') if f.is_file())
                self.size_mb = total_size // (1024 * 1024)
            except:
                pass

GAME_LIBRARY = {
    'Vanilla': GameInfo(
        name="Vanilla",
        folder_name="Y1S0_Vanilla",
        description="Y1S0; UNSTABLE, MAY CRASH ALOT",
        release_date="December 1, 2015",
        size_mb=14300,
        patch_notes=[
            "Initial release with 20 operators",
            "11 maps available at launch",
            "Terrorist Hunt and Multiplayer modes",
            "Destructible environments system",
            "Tactical realism gameplay"
        ]
    ),
    'Black Ice': GameInfo(
        name="Operation Black Ice",
        folder_name="Y1S1_BlackIce",
        description="Y1S1; Added Yacht and Canadian JTF2 Operators Buck and Frost",
        release_date="February 2, 2016",
        size_mb=16700,
        patch_notes=[
            "Added Buck (Attacker) - Skeleton Key shotgun",
            "Added Frost (Defender) - Welcome Mat traps",
            "New map: Yacht",
            "Weapon skin system introduced",
            "Ranked matchmaking improvements",
            "Various bug fixes and balancing"
        ]
    ),
    'DustLine': GameInfo(
        name="Operation Dust Line",
        folder_name="Y1S2_DustLine",
        description="Y1S2; Added Pre rework Border Navy Seals Operators Overpowered Blackbeard and Outside Black Eye Valkyrie",
        release_date="May 11, 2016",
        size_mb=20900,
        patch_notes=[
            "Added Blackbeard (Attacker) - Rifle Shield",
            "Added Valkyrie (Defender) - Black Eye cameras",
            "New map: Border",
            "Spectator camera improvements",
            "Anti-cheat system enhancements",
            "Operator balancing updates"
        ]
    ),
    'SkullRain': GameInfo(
        name="Operation Skull Rain",
        folder_name="Y1S3_SkullRain",
        description="Y1S3; Added BOPE Operators 99 Damage Pistol Caveira And Capitao, Claymores And Pre rework Favela",
        release_date="August 2, 2016",
        size_mb=25100,
        patch_notes=[
            "Added Capitão (Attacker) - Tactical crossbow",
            "Added Caveira (Defender) - Silent Step ability",
            "New map: Favela",
            "Battleye anti-cheat integration",
            "Pulse heartbeat sensor rework",
            "Lighting and visual improvements"
        ]
    ),
    'RedCrow': GameInfo(
        name="Operation Red Crow",
        folder_name="Y1S4_RedCrow",
        description="Y1S4; Added SAT Operators Hibana and Invisible drone Echo Added caliber based destructions",
        release_date="November 17, 2016",
        size_mb=28500,
        patch_notes=[
            "Added Hibana (Attacker) - X-KAIROS pellets",
            "Added Echo (Defender) - Yokai drone",
            "New map: Skyscraper",
            "Bartlett University added to multiplayer",
            "Custom games improvements",
            "Operator gadget refinements"
        ]
    ),
    'VelvetShell': GameInfo(
        name="Operation Velvet Shell",
        folder_name="Y2S1_VelvetShell",
        description="Y2S1; Added Pre rework Coastline, GEO Operators, No Glass Shattering Mira, Jackal",
        release_date="February 7, 2017",
        size_mb=33200,
        patch_notes=[
            "Added Jackal (Attacker) - Eyenox footprint scanner",
            "Added Mira (Defender) - Black Mirror windows",
            "New map: Coastline",
            "One Step Matchmaking system",
            "Alpha Pack loot system introduced",
            "Major lighting overhaul"
        ]
    ),
    'Health': GameInfo(
        name="Operation Health",
        folder_name="Y2S2_Health",
        description="Y2S2; No new content, internal Polish, hit registration improvements",
        release_date="June 7, 2017",
        size_mb=34000,
        patch_notes=[
            "Major engine improvements",
            "Hit registration fixes",
            "Server stability enhancements",
            "Network optimization",
            "Bug fixes and polish"
        ]
    ),
    'BloodOrchid': GameInfo(
        name="Operation Blood Orchid",
        folder_name="Y2S3_BloodOrchid",
        description="Y2S3: Added GROM Operator No Recoil Ela and SDU Operators Cloaked Lesion and Ying, Pre rework Theme Park",
        release_date="August 29, 2017",
        size_mb=34300,
        patch_notes=[
            "Added Ela (Defender) - Grzmot mines",
            "Added Lesion (Defender) - Gu mines",
            "Added Ying (Attacker) - Candela devices",
            "New map: Theme Park",
            "Lighting improvements",
            "Operator balancing"
        ]
    ),
    'WhiteNoise': GameInfo(
        name="Operation White Noise",
        folder_name="Y2S4_WhiteNoise",
        description="Y2S4; Added GROM Operator 2 Speed Withstand Zofia, 707th SM Battalion Operators Vigil and Dokkaebi, New map Tower",
        release_date="December 5, 2017",
        size_mb=48700,
        patch_notes=[
            "Added Zofia (Attacker) - KS79 Lifeline",
            "Added Vigil (Defender) - ERC-7 cloak",
            "Added Dokkaebi (Attacker) - Logic Bomb",
            "New map: Tower",
            "Pick and Ban system",
            "Outbreak event preparation"
        ]
    ),
    'Chimera': GameInfo(
        name="Operation Chimera",
        folder_name="Y3S1_Chimera",
        description="Y3S1; Added CBRN Operators Overpowered Lion and Finka, Outbreak Event",
        release_date="February 1, 2018",
        size_mb=58800,
        patch_notes=[
            "Added Lion (Attacker) - EE-ONE-D drone",
            "Added Finka (Defender) - Adrenal Surge",
            "Outbreak cooperative event",
            "Advanced drone deployment",
            "Weapon attachment rework",
            "UI improvements"
        ]
    ),
    'Parabellum': GameInfo(
        name="Operation ParaBellum",
        folder_name="Y3S2_ParaBellum",
        description="Y3S2; Added Alibi and Acog Maestro, Added Villa, Removed throwing back Frag Grenades",
        release_date="June 7th, 2018",
        size_mb=63300,
        patch_notes=[
            "Added Maestro (Defender) - Evil Eye cameras",
            "Added Alibi (Defender) - Prisma holograms",
            "New map: Villa",
            "Frag grenade changes",
            "Operator icon updates",
            "Sound improvements"
        ]
    ),
    'Grimsky': GameInfo(
        name="Operation GrimSky",
        folder_name="Y3S3_GrimSky",
        description="Y3S3; Added GSUTR Operators Maverick And Clash Along with Reworked Hereford Base",
        release_date="September 4, 2018",
        size_mb=72600,
        patch_notes=[
            "Added Maverick (Attacker) - Breaching torch",
            "Added Clash (Defender) - CCE Shield",
            "Hereford Base rework",
            "Dynamic resolution scaling",
            "Weapon sight misalignment fixes",
            "Deployable shield rework"
        ]
    ),
    'WindBastion': GameInfo(
        name="Operation Wind Bastion",
        folder_name="Y3S4_WindBastion",
        description="Y3S4; Added GIGR Operators Kaid and Nomad Along with The map Fortress",
        release_date="December 4, 2018",
        size_mb=76900,
        patch_notes=[
            "Added Kaid (Defender) - Rtila Electroclaw",
            "Added Nomad (Attacker) - Airjab launcher",
            "New map: Fortress",
            "Clubhouse rework",
            "Recoil system changes",
            "Operator gadget improvements"
        ]
    ),
    'BurntHorizon': GameInfo(
        name="Operation Burnt Horizon",
        folder_name="Y4S1_BurntHorizon",
        description="Y4S1; Added SASR Operators Gridlock and Mozzie Along with Pre Reworked Outback",
        release_date="March 6, 2019",
        size_mb=59700,
        patch_notes=[
            "Added Gridlock (Attacker) - Trax Stingers",
            "Added Mozzie (Defender) - Pest devices",
            "New map: Outback",
            "Capitão rework",
            "Lion rework",
            "Reverse friendly fire system"
        ]
    ),
    'PhantomSight': GameInfo(
        name="Operation Phantom Sight",
        folder_name="Y4S2_PhantomSight",
        description="Y4S2; Added Jaeger Corps Operators Warden And Nokk Along with Reworked Kafe Dostoyevsky",
        release_date="June 11, 2019",
        size_mb=67100,
        patch_notes=[
            "Added Warden (Defender) - Glance Smart Glasses",
            "Added Nøkk (Attacker) - HEL device",
            "Kafe Dostoyevsky rework",
            "IQ gadget improvements",
            "Glaz thermal scope changes",
            "Shield operator adjustments"
        ]
    ),
    'EmberRise': GameInfo(
        name="Operation Ember Rise",
        folder_name="Y4S3_EmberRise",
        description="Y4S3; Added Deployable Shield Rework and Pre rework Goyo and Amaru, Along with reworking Kanal",
        release_date="September 11, 2019",
        size_mb=69600,
        patch_notes=[
            "Added Amaru (Attacker) - Garra Hook",
            "Added Goyo (Defender) - Volcán Shield",
            "Kanal rework",
            "Deployable shield rework",
            "Clash balancing",
            "Sound occlusion improvements"
        ]
    ),
    'ShiftingTides': GameInfo(
        name="Operation Shifting Tides",
        folder_name="Y4S4_ShiftingTides",
        description="Y4S4; Added NAVYSEAL Operators Kali and Wamai Along with Theme Park rework",
        release_date="December 3, 2019",
        size_mb=75200,
        patch_notes=[
            "Added Kali (Attacker) - CSRX 300 sniper",
            "Added Wamai (Defender) - MAG-NET System",
            "Theme Park rework",
            "Twitch drone changes",
            "Lesion mine visibility",
            "Operator speed changes"
        ]
    ),
    'VoidEdge': GameInfo(
        name="Operation Void Edge",
        folder_name="Y5S1_VoidEdge",
        description="Y5S1; Added NIGHTHAVEN Operators Iana and Oryx Along with Oregon rework",
        release_date="March 10, 2020",
        size_mb=74300,
        patch_notes=[
            "Added Iana (Attacker) - Gemini Replicator",
            "Added Oryx (Defender) - Remah Dash",
            "Oregon rework",
            "Jäger balancing changes",
            "Buck skeleton key improvements",
            "Weapon sight changes"
        ]
    ),
    'SteelWave': GameInfo(
        name="Operation Steel Wave",
        folder_name="Y5S2_SteelWave",
        description="Y5S2; Added South African Operator Melusi and Norwegian Breacher Ace, House Rework",
        release_date="June 16, 2020",
        size_mb=78200,
        patch_notes=[
            "Added Ace (Attacker) – S.E.L.M.A. hard breach",
            "Added Melusi (Defender) – Banshee Sonic Defense",
            "New secondary: Proximity Alarm",
            "House map rework",
            "Amaru and Echo rework"
        ]
    ),
    'ShadowLegacy': GameInfo(
        name="Operation Shadow Legacy",
        folder_name="Y5S3_ShadowLegacy",
        description="Y5S3; Introduced Splinter Cell’s Sam Fisher (Zero), Chalet Rework, New scopes",
        release_date="September 10, 2020",
        size_mb=79900,
        patch_notes=[
            "Added Zero (Attacker) – Argus camera launcher",
            "Chalet map rework",
            "Map Ban system",
            "New scopes (1.5x, 2.0x, 3.0x) and sight changes",
            "Ping 2.0 and reinforcement pool introduced"
        ]
    ),
    'NeonDawnHM': GameInfo(
        name="Operation Neon Dawn HM Support",
        folder_name="Y5S4_NeonDawnHM",
        description="Y5S4; Heated Metal Compatible Version. Added Aruni and Skyscraper Rework",
        release_date="December 1, 2020",
        size_mb=81000,
        patch_notes=[
            "Added Aruni (Defender) – Surya Laser Gates",
            "Skyscraper map rework",
            "Jäger rework, Hibana selector update",
            "Echo drone visibility enabled",
            "Optimized for Heated Metal compatibility"
        ]
    ),
    'CrimsonHeist': GameInfo(
        name="Operation Crimson Heist",
        folder_name="Y6S1_CrimsonHeist",
        description="Y6S1; Added Argentinian Operator Flores and Border Map Rework",
        release_date="March 16, 2021",
        size_mb=83700,
        patch_notes=[
            "Added Flores (Attacker) – RCE-Ratero drones",
            "Border map rework",
            "Match Replay system (Beta)",
            "New secondary: Gonne-6",
            "Price drops for earlier operators"
        ]
    ),
    'NorthStar': GameInfo(
        name="Operation North Star",
        folder_name="Y6S2_NorthStar",
        description="Y6S2; Added Thunderbird and Favela Rework",
        release_date="June 14, 2021",
        size_mb=84200,
        patch_notes=[
            "Added Thunderbird (Defender) – Kona Station healing device",
            "Favela map rework",
            "Armor system replaced with HP system",
            "Bullet holes on soft walls rebalanced",
            "Downed Operator icon and HP displayed"
        ]
    ),
    'CrystalGuard': GameInfo(
        name="Operation Crystal Guard",
        folder_name="Y6S3_CrystalGuard",
        description="Y6S3; Added Osa, Map Tweaks, and Flashbang Improvements",
        release_date="September 7, 2021",
        size_mb=86300,
        patch_notes=[
            "Added Osa (Attacker) – Transparent Talon Shields",
            "Map updates: Coastline, Bank, Clubhouse",
            "Flashbang mechanic changes",
            "Armor rework finalization",
            "Operator balancing updates"
        ]
    ),
    'HighCalibre': GameInfo(
        name="Operation High Calibre",
        folder_name="Y6S4_HighCalibre",
        description="Y6S4; Added Thorn, Outback Map Rework, HUD overhaul",
        release_date="November 30, 2021",
        size_mb=87100,
        patch_notes=[
            "Added Thorn (Defender) – Razorbloom Shells",
            "Outback map rework",
            "New HUD interface",
            "New colorblind options",
            "Operator balancing improvements"
        ]
    ),
    'DemonVeil': GameInfo(
        name="Operation Demon Veil",
        folder_name="Y7S1_DemonVeil",
        description="Y7S1; Added Azami and Emerald Plains map",
        release_date="March 15, 2022",
        size_mb=89500,
        patch_notes=[
            "Added Azami (Defender) – Kiba Barrier foam kunai",
            "New map: Emerald Plains",
            "Attacker Repick introduced",
            "Match Replay console version",
            "Team Deathmatch mode"
        ]
    ),
    'VectorGlare': GameInfo(
        name="Operation Vector Glare",
        folder_name="Y7S2_VectorGlare",
        description="Y7S2; Added Sens, Shooting Range, Operator Guides",
        release_date="June 14, 2022",
        size_mb=89900,
        patch_notes=[
            "Added Sens (Attacker) – R.O.U. Projector System",
            "New map: Close Quarter (Team Deathmatch)",
            "Shooting Range mode",
            "Operator onboarding guides",
            "Recoil system rework"
        ]
    ),
    'BrutalSwarm': GameInfo(
        name="Operation Brutal Swarm",
        folder_name="Y7S3_BrutalSwarm",
        description="Y7S3; Added Grim and Stadium Bravo map",
        release_date="September 6, 2022",
        size_mb=91000,
        patch_notes=[
            "Added Grim (Attacker) – Kawan Hive Launcher",
            "Map pool update: Stadium Bravo returns",
            "Impact EMP added as new secondary gadget",
            "Recoil fine-tuning continued",
            "Lobby UI updates"
        ]
    ),
    'SolarRaid': GameInfo(
        name="Operation Solar Raid",
        folder_name="Y7S4_SolarRaid",
        description="Y7S4; Added Solis and Crossplay + Ranked 2.0",
        release_date="December 6, 2022",
        size_mb=93000,
        patch_notes=[
            "Added Solis (Defender) – SPEC-IO electro scanner",
            "Crossplay enabled across consoles",
            "New Ranked system (MMR replaced)",
            "New Battle Pass structure",
            "Privacy mode enhancements"
        ]
    ),
    'CommandingForce': GameInfo(
        name="Operation Commanding Force",
        folder_name="Y8S1_CommandingForce",
        description="Y8S1; Added Brava and anti-cheat enhancements",
        release_date="March 7, 2023",
        size_mb=94500,
        patch_notes=[
            "Added Brava (Attacker) – Kludge Drone to hack gadgets",
            "Reputation penalty for toxic voice chat",
            "Mouse and keyboard detection on console",
            "Reload cancel reintroduced",
            "Balancing changes: Ash, Thatcher, Mozzie"
        ]
    ),
    'DreadFactor': GameInfo(
        name="Operation Dread Factor",
        folder_name="Y8S2_DreadFactor",
        description="Y8S2; Added Fenrir and Consulate Rework",
        release_date="May 30, 2023",
        size_mb=95300,
        patch_notes=[
            "Added Fenrir (Defender) – F-NATT Fear Grenades",
            "Consulate map rework",
            "New permanent playlist: Arcade",
            "Shooting Range update with custom loadouts",
            "New gadget: Observation Blocker"
        ]
    ),
    'HeavyMettle': GameInfo(
        name="Operation Heavy Mettle",
        folder_name="Y8S3_HeavyMettle",
        description="Y8S3; Added Korean Attacker Ram and Quick Match 2.0",
        release_date="August 29, 2023",
        size_mb=96200,
        patch_notes=[
            "Added Ram (Attacker) – BU-GI Auto Breacher",
            "Quick Match 2.0 improvements",
            "Defuser timer displayed at all times",
            "Operator tutorials added",
            "Reinforcement counter UI"
        ]
    ),
    'DeepFreeze': GameInfo(
        name="Operation Deep Freeze",
        folder_name="Y8S4_DeepFreeze",
        description="Y8S4; Added Tubarão and Lair map, Frost rework",
        release_date="November 28, 2023",
        size_mb=97300,
        patch_notes=[
            "Added Tubarão (Defender) – Zoto Canisters (freeze gadgets)",
            "New map: Lair",
            "Frost Welcome Mat rework",
            "Operator loadout balancing",
            "Map filter UI changes"
        ]
    ),
    'DeadlyOmen': GameInfo(
        name="Operation Deadly Omen",
        folder_name="Y9S1_DeadlyOmen",
        description="Y9S1; Added Deimos and Reputation System Overhaul",
        release_date="March 12, 2024",
        size_mb=98400,
        patch_notes=[
            "Added Deimos (Attacker) – DeathMARK Tracker",
            "Reputation System 2.0",
            "Operator pricing adjustments",
            "Siege tutorials improved",
            "Defuser UI clarified"
        ]
    ),
    'NewBlood': GameInfo(
        name="Operation New Blood",
        folder_name="Y9S2_NewBlood",
        description="Y9S2; Recruit reworked into Striker and Sentry roles",
        release_date="June 11, 2024",
        size_mb=99100,
        patch_notes=[
            "Recruit rework: Striker (Attacker), Sentry (Defender)",
            "Map rotations updated",
            "Shield operator tweaks",
            "Aim assist refinement (console)",
            "Bug fixes and optimization"
        ]
    ),
    'PrepPhase': GameInfo(
        name="Prep Phase",
        folder_name="Y10S1_PrepPhase",
        description="Y10S1; Anniversary season – No new operator, core gameplay focus",
        release_date="July 23, 2025",
        size_mb=101000,
        patch_notes=[
            "No new operator – focus on core systems",
            "New legacy skins and bundles",
            "Operator tuning and optimization",
            "Vaulting and ADS refinements",
            "Prep for new features in Y10S2"
        ]
    ),
}


TEST_SERVER_LIBRARY = {}
try:
    for ts_name, (folder_name, manifest) in downloader.TEST_SERVERS.items():
        TEST_SERVER_LIBRARY[ts_name] = GameInfo(
            name=f"Test Server - {ts_name.split(' ')[0]}",
            folder_name=folder_name,
            description=f"Development test server build from {ts_name}",
            release_date=ts_name.split('(')[-1].replace(')', '') if '(' in ts_name else "Unknown",
            size_mb=12000,
            patch_notes=[
                "Experimental features and content",
                "Bug fixes and improvements",
                "Balance changes testing",
                "New operator testing"
            ]
        )
except:
    TEST_SERVER_LIBRARY = {
        'TTS_Build1': GameInfo(
            name="Test Server - TTS Build 1",
            folder_name="TTS_Build1",
            description="Technical Test Server build for experimental features",
            release_date="2024",
            size_mb=12000,
            patch_notes=[
                "Experimental features and content",
                "Bug fixes and improvements",
                "Balance changes testing",
                "New operator testing"
            ]
        ),
        'TTS_Build2': GameInfo(
            name="Test Server - TTS Build 2",
            folder_name="TTS_Build2",
            description="Latest Technical Test Server build",
            release_date="2024",
            size_mb=12000,
            patch_notes=[
                "Latest experimental features",
                "Advanced bug fixes",
                "New balance changes",
                "Upcoming content testing"
            ]
        )
    }

def update_installation_status():
    """Update installation status for all games"""
    for game in GAME_LIBRARY.values():
        game.check_installation(user_settings.downloads_folder)
    for game in TEST_SERVER_LIBRARY.values():
        game.check_installation(user_settings.downloads_folder)

class ModernButton(Button):
    """Professional button with improved styling"""
    def __init__(self, button_type="primary", **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        self.font_size = kwargs.get('font_size', 14)
        self.bold = True
        self.button_type = button_type
        
        color_schemes = {
            "primary": {
                'bg': COLORS['primary'],
                'text': COLORS['text_primary'],
                'hover': COLORS['primary_variant']
            },
            "secondary": {
                'bg': COLORS['secondary'],
                'text': COLORS['text_primary'],
                'hover': COLORS['hover']
            },
            "success": {
                'bg': COLORS['accent'],
                'text': COLORS['text_primary'],
                'hover': (0.0, 0.9, 0.5, 1)
            },
            "danger": {
                'bg': COLORS['error'],
                'text': COLORS['text_primary'],
                'hover': (1.0, 0.3, 0.3, 1)
            },
            "warning": {
                'bg': COLORS['warning'],
                'text': COLORS['text_primary'],
                'hover': (1.0, 0.7, 0.1, 1)
            },
            "install": {
                'bg': COLORS['accent'],
                'text': COLORS['text_primary'],
                'hover': (0.0, 0.9, 0.5, 1)
            },
            "ghost": {
                'bg': (0, 0, 0, 0),
                'text': COLORS['text_secondary'],
                'hover': COLORS['hover']
            }
        }
        
        self.color_scheme = color_schemes.get(button_type, color_schemes["primary"])
        self.color = self.color_scheme['text']
        
        with self.canvas.before:
            Color(*self.color_scheme['bg'])
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[6])
        
        self.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, *args):
        if hasattr(self, 'rect'):
            self.rect.pos = self.pos
            self.rect.size = self.size

class ModernProgressBar(ProgressBar):
    """Custom progress bar with modern styling"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        
        with self.canvas.before:
            Color(*COLORS['surface'])
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[3])
        
        with self.canvas.after:
            Color(*COLORS['primary'])
            self.progress_rect = RoundedRectangle(pos=self.pos, size=(0, self.height), radius=[3])
        
        self.bind(pos=self.update_graphics, size=self.update_graphics, value=self.update_progress)
    
    def update_graphics(self, *args):
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = self.pos
            self.bg_rect.size = self.size
        self.update_progress()
    
    def update_progress(self, *args):
        if hasattr(self, 'progress_rect'):
            progress_width = (self.value / self.max) * self.width if self.max > 0 else 0
            self.progress_rect.pos = self.pos
            self.progress_rect.size = (progress_width, self.height)

class GameCard(BoxLayout):
    """Professional game card with improved styling"""
    def __init__(self, game_info, **kwargs):
        super().__init__(**kwargs)
        self.game_info = game_info
        self.orientation = 'vertical'
        self.spacing = 0
        self.size_hint_y = None
        self.height = 300
        self.padding = [12, 12]
        
        with self.canvas.before:
            Color(*COLORS['surface'])
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
            Color(*COLORS['border'])
            self.border_line = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 8), width=1)
        
        self.bind(pos=self.update_graphics, size=self.update_graphics)
        
        self.create_content()
    
    def create_content(self):
        """Create the card content with proper layout"""
        header_layout = BoxLayout(orientation='vertical', spacing=8, size_hint_y=0.4)
        
        title_label = Label(
            text=self.game_info.name,
            font_size=16,
            bold=True,
            color=COLORS['text_primary'],
            halign='left',
            valign='center',
            text_size=(None, None),
            size_hint_y=None,
            height=40
        )
        header_layout.add_widget(title_label)
        
        info_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=25)
        
        version_label = Label(
            text=f"Version {self.game_info.version}",
            font_size=11,
            color=COLORS['text_secondary'],
            halign='left',
            text_size=(None, None)
        )
        info_layout.add_widget(version_label)
        
        date_label = Label(
            text=self.game_info.release_date,
            font_size=10,
            color=COLORS['text_disabled'],
            halign='right',
            text_size=(None, None)
        )
        info_layout.add_widget(date_label)
        
        header_layout.add_widget(info_layout)
        self.add_widget(header_layout)
        
        desc_container = BoxLayout(orientation='vertical', size_hint_y=0.3)
        
        desc_label = Label(
            text=self.game_info.description,
            font_size=11,
            color=COLORS['text_secondary'],
            text_size=(280, None),
            halign='left',
            valign='top',
            markup=True
        )
        desc_container.add_widget(desc_label)
        self.add_widget(desc_container)
        
        status_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=30)
        
        if self.game_info.is_installed:
            status_text = "INSTALLED"
            status_color = COLORS['accent']
        elif self.game_info.is_downloading:
            status_text = "DOWNLOADING"
            status_color = COLORS['primary']
        else:
            status_text = "NOT INSTALLED"
            status_color = COLORS['text_disabled']
        
        status_label = Label(
            text=status_text,
            font_size=10,
            bold=True,
            color=status_color,
            size_hint_x=0.6
        )
        status_layout.add_widget(status_label)
        
        if self.game_info.size_mb > 0:
            size_gb = self.game_info.size_mb / 1024
            size_label = Label(
                text=f"{size_gb:.1f} GB",
                font_size=10,
                color=COLORS['text_secondary'],
                halign='right',
                size_hint_x=0.4
            )
            status_layout.add_widget(size_label)
        
        self.add_widget(status_layout)
        
        if self.game_info.is_downloading:
            self.progress_bar = ModernProgressBar(
                max=100,
                value=self.game_info.download_progress,
                size_hint_y=None,
                height=6
            )
            self.add_widget(self.progress_bar)
        
        self.create_action_buttons()
    
    def create_action_buttons(self):
        """Create action buttons based on game state"""
        button_layout = BoxLayout(orientation='vertical', spacing=6, size_hint_y=0.3)
        
        if self.game_info.is_installed:
            launch_btn = ModernButton(
                text="LAUNCH",
                button_type="success",
                size_hint_y=None,
                height=35
            )
            launch_btn.bind(on_press=lambda x: self.launch_game())
            button_layout.add_widget(launch_btn)
            
            secondary_layout = BoxLayout(orientation='horizontal', spacing=6, size_hint_y=None, height=28)
            
            patch_btn = ModernButton(
                text="PATCH NOTES",
                button_type="ghost",
                font_size=9
            )
            patch_btn.bind(on_press=lambda x: self.show_patch_notes())
            secondary_layout.add_widget(patch_btn)
            
            manage_btn = ModernButton(
                text="MANAGE",
                button_type="ghost",
                font_size=9
            )
            manage_btn.bind(on_press=lambda x: self.show_manage_options())
            secondary_layout.add_widget(manage_btn)
            
            button_layout.add_widget(secondary_layout)
            
        elif self.game_info.is_downloading:
            cancel_btn = ModernButton(
                text="CANCEL",
                button_type="danger",
                size_hint_y=None,
                height=35
            )
            cancel_btn.bind(on_press=lambda x: self.cancel_download())
            button_layout.add_widget(cancel_btn)
            
        else:
            install_btn = ModernButton(
                text="INSTALL",
                button_type="install",
                size_hint_y=None,
                height=35
            )
            install_btn.bind(on_press=lambda x: self.install_game())
            button_layout.add_widget(install_btn)
            
            if self.game_info.patch_notes:
                patch_btn = ModernButton(
                    text="VIEW PATCH NOTES",
                    button_type="ghost",
                    size_hint_y=None,
                    height=25,
                    font_size=9
                )
                patch_btn.bind(on_press=lambda x: self.show_patch_notes())
                button_layout.add_widget(patch_btn)
        
        self.add_widget(button_layout)
    
    def update_graphics(self, *args):
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = self.pos
            self.bg_rect.size = self.size
        if hasattr(self, 'border_line'):
            self.border_line.rounded_rectangle = (self.x, self.y, self.width, self.height, 8)
    
    def show_patch_notes(self):
        """Show patch notes with fixed layout"""
        try:
            layout = BoxLayout(orientation='vertical', spacing=15, padding=20)
            
            
            header = BoxLayout(orientation='vertical', spacing=8, size_hint_y=None, height=80)
            
            title_label = Label(
                text=f"{self.game_info.name} - Patch Notes",
                font_size=18,
                bold=True,
                color=COLORS['primary'],
                size_hint_y=None,
                height=35,
                text_size=(None, None)
            )
            header.add_widget(title_label)
            
            date_label = Label(
                text=f"Released: {self.game_info.release_date}",
                font_size=12,
                color=COLORS['text_secondary'],
                size_hint_y=None,
                height=25,
                text_size=(None, None)
            )
            header.add_widget(date_label)
            
            layout.add_widget(header)
            
            scroll = ScrollView()
            
            notes_layout = BoxLayout(orientation='vertical', spacing=8, size_hint_y=None, padding=[10, 10])
            notes_layout.bind(minimum_height=notes_layout.setter('height'))
            
            if hasattr(self.game_info, 'patch_notes') and self.game_info.patch_notes:
                for note in self.game_info.patch_notes:
                    try:
                        note_label = Label(
                            text=f"• {str(note)}", 
                            font_size=12,
                            color=COLORS['text_primary'],
                            text_size=(450, None),
                            halign='left',
                            valign='top',
                            size_hint_y=None
                        )
                        note_label.bind(texture_size=note_label.setter('height'))
                        notes_layout.add_widget(note_label)
                    except Exception as note_error:
                        print(f"Error adding patch note: {note_error}")
                        continue
            else:
                no_notes_label = Label(
                    text="No patch notes available for this version.",
                    font_size=12,
                    color=COLORS['text_secondary'],
                    text_size=(450, None),
                    halign='center',
                    valign='center',
                    size_hint_y=None,
                    height=50
                )
                notes_layout.add_widget(no_notes_label)
            
            scroll.add_widget(notes_layout)
            layout.add_widget(scroll)
            
            close_btn = ModernButton(
                text="Close",
                button_type="secondary",
                size_hint=(None, None),
                size=(100, 35),
                pos_hint={'center_x': 0.5}
            )
            layout.add_widget(close_btn)
            
            popup = Popup(
                title="",
                content=layout,
                size_hint=(0.7, 0.7),
                auto_dismiss=True
            )
            
            close_btn.bind(on_press=lambda x: popup.dismiss())
            popup.open()
            
        except Exception as e:
            print(f"Error showing patch notes: {e}")
            self.show_alert("Error", f"Could not display patch notes: {str(e)}")
    
    def launch_game(self):
        """Launch the installed game"""
        if self.game_info.install_path:
            try:
                install_path = Path(self.game_info.install_path)
                exe_files = list(install_path.glob("*.exe"))
                
                if exe_files:
                    os.startfile(str(exe_files[0]))
                else:
                    os.startfile(str(install_path))
                    
            except Exception as e:
                self.show_alert("Launch Error", f"Could not launch game: {str(e)}")
    
    def install_game(self):
        """Start installation process"""
        if not user_settings.username:
            self.show_alert("Missing Credentials", "Please configure your Steam credentials in Settings first!")
            return
        
        self.game_info.is_downloading = True
        self.game_info.download_progress = 0
        
        app = App.get_running_app()
        library_screen = app.root.get_screen('library')
        library_screen.refresh_library()
        
        if self.game_info.name.startswith("Rainbow Six Siege") or self.game_info.name.startswith("Operation"):
            season_key = None
            for key, game in GAME_LIBRARY.items():
                if game == self.game_info:
                    season_key = key
                    break
            if season_key:
                library_screen.download_game(season_key, self)
        else:
            ts_key = None
            for key, game in TEST_SERVER_LIBRARY.items():
                if game == self.game_info:
                    ts_key = key
                    break
            if ts_key:
                library_screen.download_test_server(ts_key, self)
    
    def cancel_download(self):
        """Cancel ongoing download"""
        self.game_info.is_downloading = False
        self.game_info.download_progress = 0
        
        app = App.get_running_app()
        library_screen = app.root.get_screen('library')
        library_screen.refresh_library()
        
        self.show_alert("Download Cancelled", "The download has been cancelled successfully.")
    
    def show_manage_options(self):
        """Show management options for installed game"""
        layout = BoxLayout(orientation='vertical', spacing=15, padding=20)
        
        title = Label(
            text=f"Manage {self.game_info.name}",
            font_size=16,
            bold=True,
            color=COLORS['primary'],
            size_hint_y=None,
            height=35
        )
        layout.add_widget(title)
        
        options_layout = BoxLayout(orientation='vertical', spacing=10)
        
        folder_btn = ModernButton(
            text="Open Install Folder",
            button_type="secondary",
            size_hint_y=None,
            height=40
        )
        folder_btn.bind(on_press=lambda x: [popup.dismiss(), os.startfile(self.game_info.install_path)])
        options_layout.add_widget(folder_btn)
        
        config_btn = ModernButton(
            text="Edit Configuration",
            button_type="primary",
            size_hint_y=None,
            height=40
        )
        config_btn.bind(on_press=lambda x: [popup.dismiss(), self.show_config_editor()])
        options_layout.add_widget(config_btn)
        
        uninstall_btn = ModernButton(
            text="Uninstall",
            button_type="danger",
            size_hint_y=None,
            height=40
        )
        uninstall_btn.bind(on_press=lambda x: [popup.dismiss(), self.confirm_uninstall()])
        options_layout.add_widget(uninstall_btn)
        
        layout.add_widget(options_layout)
        
        close_btn = ModernButton(
            text="Close",
            button_type="secondary",
            size_hint=(None, None),
            size=(100, 35),
            pos_hint={'center_x': 0.5}
        )
        layout.add_widget(close_btn)
        
        popup = Popup(
            title="",
            content=layout,
            size_hint=(0.4, 0.5),
            auto_dismiss=True
        )
        
        close_btn.bind(on_press=lambda x: popup.dismiss())
        popup.open()
    
    def show_config_editor(self):
        """Show configuration editor"""
        if not self.game_info.install_path:
            return
        
        config_files = ConfigEditor.find_config_files(self.game_info.install_path)
        
        if not config_files:
            self.show_alert("No Config Files", "No configuration files found in the installation directory.")
            return
        
        layout = BoxLayout(orientation='vertical', spacing=15, padding=20)
        
        title = Label(
            text="Configuration Editor",
            font_size=16,
            bold=True,
            color=COLORS['primary'],
            size_hint_y=None,
            height=35
        )
        layout.add_widget(title)
        
        username_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=45)
        
        username_label = Label(
            text="Game Username:",
            font_size=12,
            color=COLORS['text_primary'],
            size_hint_x=None,
            width=120
        )
        username_layout.add_widget(username_label)
        
        username_input = TextInput(
            text=user_settings.game_username,
            font_size=12,
            multiline=False,
            size_hint_y=None,
            height=35,
            background_color=COLORS['surface'],
            foreground_color=COLORS['text_primary']
        )
        username_layout.add_widget(username_input)
        
        layout.add_widget(username_layout)
        
        button_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=40)
        
        cancel_btn = ModernButton(
            text="Cancel",
            button_type="secondary",
            size_hint=(0.5, None),
            height=35
        )
        
        apply_btn = ModernButton(
            text="Apply",
            button_type="success",
            size_hint=(0.5, None),
            height=35
        )
        
        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(apply_btn)
        layout.add_widget(button_layout)
        
        popup = Popup(
            title="",
            content=layout,
            size_hint=(0.5, 0.4),
            auto_dismiss=True
        )
        
        def apply_changes(instance):
            new_username = username_input.text.strip()
            if not new_username:
                self.show_alert("Invalid Username", "Please enter a valid username.")
                return
            
            success_count = 0
            for config_file in config_files:
                content = ConfigEditor.read_config_file(config_file)
                if content:
                    updated_content = ConfigEditor.update_username_in_config(content, new_username)
                    if ConfigEditor.write_config_file(config_file, updated_content):
                        success_count += 1
            
            popup.dismiss()
            if success_count > 0:
                self.show_alert("Configuration Updated", 
                              f"Successfully updated {success_count} config file(s) with username: {new_username}")
        
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        apply_btn.bind(on_press=apply_changes)
        
        popup.open()
    
    def confirm_uninstall(self):
        """Confirm uninstallation"""
        layout = BoxLayout(orientation='vertical', spacing=15, padding=20)
        
        warning = Label(
            text=f"Are you sure you want to uninstall {self.game_info.name}?\n\nThis will permanently delete all game files.",
            color=COLORS['warning'],
            text_size=(350, None),
            halign='center',
            font_size=12
        )
        layout.add_widget(warning)
        
        button_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=40)
        
        cancel_btn = ModernButton(
            text="Cancel",
            button_type="secondary",
            size_hint=(0.5, None),
            height=35
        )
        
        uninstall_btn = ModernButton(
            text="Uninstall",
            button_type="danger",
            size_hint=(0.5, None),
            height=35
        )
        
        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(uninstall_btn)
        layout.add_widget(button_layout)
        
        popup = Popup(
            title="",
            content=layout,
            size_hint=(0.4, 0.3),
            auto_dismiss=False
        )
        
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        uninstall_btn.bind(on_press=lambda x: [popup.dismiss(), self.uninstall_game()])
        
        popup.open()
    
    def uninstall_game(self):
        """Uninstall the game"""
        try:
            import shutil
            if self.game_info.install_path and Path(self.game_info.install_path).exists():
                shutil.rmtree(self.game_info.install_path)
                
                self.game_info.is_installed = False
                self.game_info.install_path = None
                
                app = App.get_running_app()
                library_screen = app.root.get_screen('library')
                library_screen.refresh_library()
                
                self.show_alert("Uninstall Complete", f"{self.game_info.name} has been uninstalled successfully.")
            
        except Exception as e:
            self.show_alert("Uninstall Error", f"Failed to uninstall game: {str(e)}")
    
    def update_download_progress(self, progress):
        """Update download progress"""
        self.game_info.download_progress = progress
        if hasattr(self, 'progress_bar'):
            Clock.schedule_once(lambda dt: setattr(self.progress_bar, 'value', progress))
    
    def show_alert(self, title, message):
        """Show alert dialog"""
        layout = BoxLayout(orientation='vertical', spacing=15, padding=20)
        
        title_label = Label(
            text=title,
            font_size=16,
            bold=True,
            color=COLORS['primary'],
            size_hint_y=None,
            height=30
        )
        layout.add_widget(title_label)
        
        msg_label = Label(
            text=message,
            color=COLORS['text_primary'],
            text_size=(400, None),
            halign='center',
            font_size=12
        )
        layout.add_widget(msg_label)
        
        ok_btn = ModernButton(
            text="OK",
            button_type="primary",
            size_hint=(None, None),
            size=(100, 35),
            pos_hint={'center_x': 0.5}
        )
        layout.add_widget(ok_btn)
        
        popup = Popup(
            title="",
            content=layout,
            size_hint=(0.5, 0.3)
        )
        
        ok_btn.bind(on_press=lambda x: popup.dismiss())
        popup.open()

class ProgressDialog(Popup):
    """Professional progress dialog"""
    def __init__(self, title="Installing...", game_card=None, **kwargs):
        self.title_text = title
        self.progress_value = 0
        self.status_text = "Preparing installation..."
        self.is_open = False
        self.game_card = game_card
        self.is_cancelled = False
    
    def create_popup(self):
        """Create the popup in the main thread"""
        def create_ui(dt):
            layout = BoxLayout(orientation='vertical', spacing=20, padding=25)
            
            title_label = Label(
                text=self.title_text,
                font_size=18,
                bold=True,
                color=COLORS['text_primary'],
                size_hint_y=None,
                height=35
            )
            layout.add_widget(title_label)
            
            self.status_label = Label(
                text=self.status_text,
                font_size=12,
                color=COLORS['text_secondary'],
                size_hint_y=None,
                height=25
            )
            layout.add_widget(self.status_label)
            
            progress_container = BoxLayout(orientation='vertical', spacing=8, size_hint_y=None, height=50)
            
            self.progress = ModernProgressBar(
                max=100,
                value=self.progress_value,
                size_hint_y=None,
                height=8
            )
            progress_container.add_widget(self.progress)
            
            self.progress_text = Label(
                text=f"{self.progress_value:.1f}%",
                font_size=12,
                bold=True,
                color=COLORS['primary'],
                size_hint_y=None,
                height=25
            )
            progress_container.add_widget(self.progress_text)
            
            layout.add_widget(progress_container)
            
            self.cancel_btn = ModernButton(
                text="Cancel",
                button_type="danger",
                size_hint=(None, None),
                size=(120, 35),
                pos_hint={'center_x': 0.5}
            )
            self.cancel_btn.bind(on_press=self.cancel_download)
            layout.add_widget(self.cancel_btn)
            
            self.popup = Popup(
                title="",
                content=layout,
                size_hint=(0.5, 0.4),
                auto_dismiss=False
            )
            
            self.popup.open()
            self.is_open = True
        
        Clock.schedule_once(create_ui)
    
    def update_progress(self, value, status="Installing..."):
        """Thread-safe progress update"""
        self.progress_value = value
        self.status_text = status
        
        def update_ui(dt):
            if hasattr(self, 'progress') and self.is_open and not self.is_cancelled:
                self.progress.value = value
                self.progress_text.text = f"{value:.1f}%"
                self.status_label.text = status
                if self.game_card:
                    self.game_card.update_download_progress(value)
        
        Clock.schedule_once(update_ui)
    
    def cancel_download(self, instance):
        """Handle download cancellation"""
        self.is_cancelled = True
        self.cancel_btn.text = "Cancelling..."
        self.cancel_btn.disabled = True
        self.update_progress(self.progress_value, "Cancelling download...")
        Clock.schedule_once(lambda dt: self.close_dialog(), 1.0)
    
    def close_dialog(self):
        """Thread-safe dialog closing"""
        def close_ui(dt):
            if hasattr(self, 'popup') and self.is_open:
                self.popup.dismiss()
                self.is_open = False
        Clock.schedule_once(close_ui)

def threaded(func):
    """Run blocking function in a thread."""
    def wrapper(*args, **kwargs):
        threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True).start()
    return wrapper

class LibraryScreen(Screen):
    """Professional library screen with tabs"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_ui()
    
    def create_ui(self):
        main_layout = BoxLayout(orientation='vertical', spacing=0)
        
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, padding=[20, 10])
        
        with header.canvas.before:
            Color(*COLORS['surface'])
            self.header_bg = Rectangle(pos=header.pos, size=header.size)
            Color(*COLORS['border'])
            self.header_line = Line(points=[header.x, header.y, header.x + header.width, header.y], width=1)
        
        header.bind(pos=self.update_header_graphics, size=self.update_header_graphics)
        
        title_section = BoxLayout(orientation='vertical')
        
        library_title = Label(
            text="T's Downloader",
            font_size=20,
            bold=True,
            color=COLORS['text_primary'],
            halign='left'
        )
        title_section.add_widget(library_title)
        
        subtitle = Label(
            text="Legacy Versions & Test Servers",
            font_size=11,
            color=COLORS['text_secondary'],
            halign='left'
        )
        title_section.add_widget(subtitle)
        
        header.add_widget(title_section)
        header.add_widget(Widget()) 
        
        controls_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_x=None, width=220)
        
        refresh_btn = ModernButton(
            text="Refresh",
            button_type="secondary",
            size_hint_x=None,
            width=80,
            height=35
        )
        refresh_btn.bind(on_press=lambda x: self.refresh_library())
        controls_layout.add_widget(refresh_btn)
        
        settings_btn = ModernButton(
            text="Settings",
            button_type="primary",
            size_hint_x=None,
            width=80,
            height=35
        )
        settings_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'settings'))
        controls_layout.add_widget(settings_btn)
        
        header.add_widget(controls_layout)
        main_layout.add_widget(header)
        
        self.tab_panel = TabbedPanel(
            do_default_tab=False,
            tab_pos='top_left',
            tab_height=40
        )
        
        self.tab_panel.background_color = COLORS['background']
        
        self.create_versions_tab()
        self.create_patches_tab()
        self.create_tools_tab()
        self.create_modding_tab()
        
        main_layout.add_widget(self.tab_panel)
        self.add_widget(main_layout)
    
    def create_versions_tab(self):
        """Create the Versions tab"""
        versions_tab = TabbedPanelItem(text='Versions')
        
        content_scroll = ScrollView()
        content_layout = GridLayout(cols=4, spacing=15, padding=20, size_hint_y=None)
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        self.versions_content_layout = content_layout
        
        Window.bind(on_resize=self.update_grid_cols)
        
        self.refresh_versions_tab()
        
        content_scroll.add_widget(content_layout)
        versions_tab.add_widget(content_scroll)
        self.tab_panel.add_widget(versions_tab)
        
        self.tab_panel.default_tab = versions_tab
    

    
    def create_patches_tab(self):
        """Create the Patches tab with HeatedMetal support"""
        patches_tab = TabbedPanelItem(text='Patches')
        
        main_layout = BoxLayout(orientation='vertical', padding=25, spacing=20)
        
        header_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height=80)
        

        title_label = Label(
            text="HEATED METAL PATCHES",
            font_size=18,
            bold=True,
            color=COLORS['primary'],
            size_hint_y=None,
            height=35,
            halign='left'
        )
        header_layout.add_widget(title_label)
        
        desc_label = Label(
            text="Download Custom Modding Tool Heated Metal",
            font_size=12,
            color=COLORS['text_secondary'],
            size_hint_y=None,
            height=25,
            halign='left'
        )
        header_layout.add_widget(desc_label)
        
        main_layout.add_widget(header_layout)
        
        patch_card = BoxLayout(orientation='vertical', spacing=15, size_hint_y=None, height=200, padding=20)
        
        with patch_card.canvas.before:
            Color(*COLORS['surface'])
            patch_card.bg_rect = RoundedRectangle(pos=patch_card.pos, size=patch_card.size, radius=[8])
            Color(*COLORS['border'])
            patch_card.border_line = Line(rounded_rectangle=(patch_card.x, patch_card.y, patch_card.width, patch_card.height, 8), width=1)
        
        patch_card.bind(pos=lambda *args: [setattr(patch_card.bg_rect, 'pos', patch_card.pos), 
                                         setattr(patch_card.border_line, 'rounded_rectangle', (patch_card.x, patch_card.y, patch_card.width, patch_card.height, 8))],
                       size=lambda *args: [setattr(patch_card.bg_rect, 'size', patch_card.size),
                                          setattr(patch_card.border_line, 'rounded_rectangle', (patch_card.x, patch_card.y, patch_card.width, patch_card.height, 8))])
        
        patch_title = Label(
            text="HeatedMetal v0.2.3",
            font_size=16,
            bold=True,
            color=COLORS['text_primary'],
            size_hint_y=None,
            height=30,
            halign='left'
        )
        patch_card.add_widget(patch_title)
        
        patch_desc = Label(
            text="Modding SDK For Neon Dawn (HEATEDMETAL SUPPORT)",
            font_size=12,
            color=COLORS['text_secondary'],
            text_size=(None, None),
            size_hint_y=None,
            height=40,
            halign='left'
        )
        patch_card.add_widget(patch_desc)
        
        download_btn = ModernButton(
            text="DOWNLOAD HEATEDMETAL",
            button_type="install",
            size_hint_y=None,
            height=40
        )
        download_btn.bind(on_press=lambda x: self.download_heated_metal())
        patch_card.add_widget(download_btn)
        
        main_layout.add_widget(patch_card)
        main_layout.add_widget(Widget()) 
        

        
        patches_tab.add_widget(main_layout)
        self.tab_panel.add_widget(patches_tab)
    
    def create_tools_tab(self):
        """Create the Tools tab with tool downloads"""
        tools_tab = TabbedPanelItem(text='Tools')
        
        main_layout = BoxLayout(orientation='vertical', padding=25, spacing=20)
        
        header_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height=80)
        
        title_label = Label(
            text="ADDITIONAL TOOLS",
            font_size=18,
            bold=True,
            color=COLORS['primary'],
            size_hint_y=None,
            height=35,
            halign='left'
        )
        header_layout.add_widget(title_label)
        
        desc_label = Label(
            text="Download useful tools and utilities for Rainbow Six Siege",
            font_size=12,
            color=COLORS['text_secondary'],
            size_hint_y=None,
            height=25,
            halign='left'
        )
        header_layout.add_widget(desc_label)
        
        main_layout.add_widget(header_layout)
        
        tools_scroll = ScrollView()
        tools_layout = GridLayout(cols=2, spacing=15, size_hint_y=None, padding=10)
        tools_layout.bind(minimum_height=tools_layout.setter('height'))
        
        liberator_card = self.create_tool_card(
            "R6 Liberator",
            "Manifest tool for Rainbow Six Siege",
            "v0.0.0.22",
            lambda: self.download_liberator()
        )
        tools_layout.add_widget(liberator_card)
        
        dxvk_card = self.create_tool_card(
            "Siege DXVK",
            "DirectX to Vulkan translation layer for better performance",
            "Latest",
            lambda: self.download_dxvk()
        )
        tools_layout.add_widget(dxvk_card)
        
        tools_scroll.add_widget(tools_layout)
        main_layout.add_widget(tools_scroll)
        
        tools_tab.add_widget(main_layout)
        self.tab_panel.add_widget(tools_tab)
    
    def create_tool_card(self, name, description, version, download_callback):
        """Create a tool card"""
        card = BoxLayout(orientation='vertical', spacing=12, size_hint_y=None, height=150, padding=15)
        
        with card.canvas.before:
            Color(*COLORS['surface'])
            card.bg_rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[8])
            Color(*COLORS['border'])
            card.border_line = Line(rounded_rectangle=(card.x, card.y, card.width, card.height, 8), width=1)
        
        card.bind(pos=lambda *args: [setattr(card.bg_rect, 'pos', card.pos), 
                                   setattr(card.border_line, 'rounded_rectangle', (card.x, card.y, card.width, card.height, 8))],
                 size=lambda *args: [setattr(card.bg_rect, 'size', card.size),
                                    setattr(card.border_line, 'rounded_rectangle', (card.x, card.y, card.width, card.height, 8))])
        
        title_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=25)
        
        title_label = Label(
            text=name,
            font_size=14,
            bold=True,
            color=COLORS['text_primary'],
            halign='left'
        )
        title_layout.add_widget(title_label)
        
        version_label = Label(
            text=version,
            font_size=10,
            color=COLORS['text_disabled'],
            size_hint_x=None,
            width=60,
            halign='right'
        )
        title_layout.add_widget(version_label)
        
        card.add_widget(title_layout)
        
        desc_label = Label(
            text=description,
            font_size=11,
            color=COLORS['text_secondary'],
            text_size=(None, None),
            size_hint_y=None,
            height=40,
            halign='left'
        )
        card.add_widget(desc_label)
        
        download_btn = ModernButton(
            text="DOWNLOAD",
            button_type="primary",
            size_hint_y=None,
            height=35
        )
        download_btn.bind(on_press=lambda x: download_callback())
        card.add_widget(download_btn)
        
        return card
    
    def create_modding_tab(self):
        """Create the Modding tab"""
        modding_tab = TabbedPanelItem(text='Modding')
        
        empty_layout = BoxLayout(orientation='vertical', padding=50)
        
        empty_label = Label(
            text="Modding support coming soon...",
            font_size=16,
            color=COLORS['text_secondary'],
            halign='center'
        )
        empty_layout.add_widget(empty_label)
        
        modding_tab.add_widget(empty_layout)
        self.tab_panel.add_widget(modding_tab)
    
    def update_grid_cols(self, instance, width, height):
        """Update grid columns based on window width"""
        if hasattr(self, 'versions_content_layout'):
            if width < 1000:
                self.versions_content_layout.cols = 2
            elif width < 1400:
                self.versions_content_layout.cols = 3
            else:
                self.versions_content_layout.cols = 4
    
    def update_header_graphics(self, instance, value):
        """Update header graphics"""
        if hasattr(self, 'header_bg'):
            self.header_bg.pos = instance.pos
            self.header_bg.size = instance.size
        if hasattr(self, 'header_line'):
            self.header_line.points = [instance.x, instance.y, instance.x + instance.width, instance.y]
    
    def refresh_library(self):
        """Refresh the library view"""
        self.refresh_versions_tab()
    
    def refresh_versions_tab(self):
        """Refresh the versions tab content"""
        update_installation_status()
        
        if hasattr(self, 'versions_content_layout'):
            self.versions_content_layout.clear_widgets()
            
            games = list(GAME_LIBRARY.values())
            
            games.sort(key=lambda x: (not x.is_installed, x.release_date))
            
            for game_info in games:
                game_card = GameCard(game_info, size_hint_x=None, width=300)
                self.versions_content_layout.add_widget(game_card)
    

    
    @threaded
    def download_heated_metal(self):
        """Download HeatedMetal patches"""
        progress_dialog = ProgressDialog("Downloading HeatedMetal...")
        progress_dialog.create_popup()
        
        try:
            progress_dialog.update_progress(10, "Connecting to GitHub...")
            
            success, message = PatchManager.download_heated_metal()
            
            if success:
                progress_dialog.update_progress(100, "HeatedMetal installed successfully!")
                Clock.schedule_once(lambda dt: self._show_success("HeatedMetal Downloaded", message), 1.5)
            else:
                Clock.schedule_once(lambda dt: self._show_error("Download Failed", message))
            
        except Exception as e:
            Clock.schedule_once(lambda dt: self._show_error("Download Error", f"Failed to download HeatedMetal: {str(e)}"))
        finally:
            progress_dialog.close_dialog()
    
    @threaded
    def download_liberator(self):
        """Download R6 Liberator"""
        progress_dialog = ProgressDialog("Downloading R6 Liberator...")
        progress_dialog.create_popup()
        
        try:
            progress_dialog.update_progress(10, "Connecting to download server...")
            
            success, message = ToolManager.download_liberator()
            
            if success:
                progress_dialog.update_progress(100, "R6 Liberator downloaded successfully!")
                Clock.schedule_once(lambda dt: self._show_success("R6 Liberator Downloaded", message), 1.5)
            else:
                Clock.schedule_once(lambda dt: self._show_error("Download Failed", message))
            
        except Exception as e:
            Clock.schedule_once(lambda dt: self._show_error("Download Error", f"Failed to download R6 Liberator: {str(e)}"))
        finally:
            progress_dialog.close_dialog()
    
    @threaded
    def download_dxvk(self):
        """Download Siege DXVK"""
        progress_dialog = ProgressDialog("Downloading Siege DXVK...")
        progress_dialog.create_popup()
        
        try:
            progress_dialog.update_progress(10, "Connecting to download server...")
            
            success, message = ToolManager.download_dxvk()
            
            if success:
                progress_dialog.update_progress(100, "Siege DXVK installed successfully!")
                Clock.schedule_once(lambda dt: self._show_success("Siege DXVK Downloaded", message), 1.5)
            else:
                Clock.schedule_once(lambda dt: self._show_error("Download Failed", message))
            
        except Exception as e:
            Clock.schedule_once(lambda dt: self._show_error("Download Error", f"Failed to download Siege DXVK: {str(e)}"))
        finally:
            progress_dialog.close_dialog()
    
    @threaded
    def download_game(self, season_key, game_card=None):
        """Download a game season"""
        progress_dialog = ProgressDialog(f"Installing {GAME_LIBRARY[season_key].name}", game_card)
        progress_dialog.create_popup()
        
        try:
            progress_dialog.update_progress(5, "Initializing installation...")
            
            downloader.DOWNLOADS_DIR = Path(user_settings.downloads_folder)
            
            progress_dialog.update_progress(15, "Connecting to download servers...")
            
            import time
            for i in range(20, 90, 10):
                if progress_dialog.is_cancelled:
                    return
                progress_dialog.update_progress(i, f"Installing... {i}%")
                time.sleep(0.3)
            
            progress_dialog.update_progress(90, "Finalizing installation...")
            
            downloader.download_season(season_key)
            
            progress_dialog.update_progress(100, "Installation complete!")
            
            Clock.schedule_once(lambda dt: self._download_complete(progress_dialog, season_key), 1.5)
            
        except Exception as e:
            if not progress_dialog.is_cancelled:
                Clock.schedule_once(lambda dt: self._download_error(progress_dialog, str(e)))
    

class SettingsScreen(Screen):
    """Professional settings screen"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_ui()
    
    def create_ui(self):
        main_layout = BoxLayout(orientation='vertical', spacing=0)
        
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, padding=[20, 10])
        
        with header.canvas.before:
            Color(*COLORS['surface'])
            self.header_bg = Rectangle(pos=header.pos, size=header.size)
            Color(*COLORS['border'])
            self.header_line = Line(points=[header.x, header.y, header.x + header.width, header.y], width=1)
        
        header.bind(pos=self.update_header_graphics, size=self.update_header_graphics)
        
        back_btn = ModernButton(
            text='Back to Library',
            button_type="secondary",
            size_hint=(None, None),
            size=(140, 35)
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'library'))
        header.add_widget(back_btn)
        
        title_section = BoxLayout(orientation='vertical')
        
        title = Label(
            text="SETTINGS",
            font_size=20,
            bold=True,
            color=COLORS['text_primary'],
            halign='left'
        )
        title_section.add_widget(title)
        
        subtitle = Label(
            text="Configure your downloader preferences",
            font_size=11,
            color=COLORS['text_secondary'],
            halign='left'
        )
        title_section.add_widget(subtitle)
        
        header.add_widget(title_section)
        header.add_widget(Widget())  
        
        main_layout.add_widget(header)
        
        scroll = ScrollView()
        settings_layout = BoxLayout(orientation='vertical', spacing=25, padding=25, size_hint_y=None)
        settings_layout.bind(minimum_height=settings_layout.setter('height'))
        
        account_section = self.create_settings_section("STEAM ACCOUNT", [
            self.create_text_setting("Steam Username", "username", "Your Steam login username"),
            self.create_password_setting("Password", "password", "Leave empty to use Steam login prompt"),
            self.create_switch_setting("Remember Password", "remember_password", "Save password securely for future use")
        ])
        settings_layout.add_widget(account_section)
        
        config_section = self.create_settings_section("GAME CONFIGURATION", [
            self.create_text_setting("Default Game Username", "game_username", "Username for game configuration files"),
            self.create_switch_setting("Auto-configure Games", "auto_configure", "Automatically configure games after installation")
        ])
        settings_layout.add_widget(config_section)
        
        download_section = self.create_settings_section("DOWNLOAD SETTINGS", [
            self.create_slider_setting("Max Concurrent Downloads", "max_downloads", 1, 50, 1),
            self.create_switch_setting("Auto-start Downloads", "auto_start_downloads", "Start downloads immediately after clicking install"),
            self.create_folder_setting("Downloads Folder", "downloads_folder", "Choose where games are installed")
        ])
        settings_layout.add_widget(download_section)
        
        resources_section = self.create_settings_section("RESOURCES", [
            self.create_folder_setting("Resources Folder", "resources_folder", "Choose where tools and resources are stored"),
            self.create_switch_setting("Auto-download Resources", "auto_download_resources", "Automatically download required resources"),
            self.create_switch_setting("Check Resources on Startup", "check_resources_on_startup", "Verify resources are available when starting the app"),
            self.create_button_setting("Setup Resources Now", "Download and setup all required resources", lambda: self.setup_resources())
        ])
        settings_layout.add_widget(resources_section)
        
        interface_section = self.create_settings_section("INTERFACE", [
            self.create_switch_setting("Show Patch Notes", "show_patch_notes", "Display patch notes button on game cards")
        ])
        settings_layout.add_widget(interface_section)
        
        save_btn = ModernButton(
            text='SAVE SETTINGS',
            button_type="success",
            size_hint_y=None,
            height=50,
            font_size=16
        )
        save_btn.bind(on_press=self.save_settings)
        settings_layout.add_widget(save_btn)
        
        scroll.add_widget(settings_layout)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
    
    def update_header_graphics(self, instance, value):
        """Update header graphics"""
        if hasattr(self, 'header_bg'):
            self.header_bg.pos = instance.pos
            self.header_bg.size = instance.size
        if hasattr(self, 'header_line'):
            self.header_line.points = [instance.x, instance.y, instance.x + instance.width, instance.y]
    
    def create_settings_section(self, title, settings_widgets):
        """Create a settings section"""
        section = BoxLayout(orientation='vertical', spacing=15, size_hint_y=None)
        section.bind(minimum_height=section.setter('height'))
        
        with section.canvas.before:
            Color(*COLORS['surface_variant'])
            section.bg_rect = RoundedRectangle(pos=section.pos, size=section.size, radius=[8])
            Color(*COLORS['border'])
            section.border_line = Line(rounded_rectangle=(section.x, section.y, section.width, section.height, 8), width=1)
        
        section.bind(pos=lambda *args: [setattr(section.bg_rect, 'pos', section.pos), 
                                      setattr(section.border_line, 'rounded_rectangle', (section.x, section.y, section.width, section.height, 8))],
                    size=lambda *args: [setattr(section.bg_rect, 'size', section.size),
                                       setattr(section.border_line, 'rounded_rectangle', (section.x, section.y, section.width, section.height, 8))])
        
        section.padding = [20, 15]
        
        title_label = Label(
            text=title,
            font_size=16,
            bold=True,
            color=COLORS['primary'],
            size_hint_y=None,
            height=30,
            halign='left'
        )
        section.add_widget(title_label)
        
        for widget in settings_widgets:
            section.add_widget(widget)
        
        return section
    
    def create_text_setting(self, label, setting_key, hint):
        """Create a text input setting"""
        container = BoxLayout(orientation='vertical', spacing=8, size_hint_y=None, height=75)
        
        label_widget = Label(
            text=label,
            font_size=12,
            bold=True,
            color=COLORS['text_primary'],
            size_hint_y=None,
            height=25,
            halign='left'
        )
        container.add_widget(label_widget)
        
        text_input = TextInput(
            text=getattr(user_settings, setting_key),
            hint_text=hint,
            multiline=False,
            size_hint_y=None,
            height=35,
            background_color=COLORS['background'],
            foreground_color=COLORS['text_primary'],
            cursor_color=COLORS['primary'],
            font_size=12,
            padding=[10, 8]
        )
        
        setattr(self, f"{setting_key}_input", text_input)
        container.add_widget(text_input)
        return container
    
    def create_password_setting(self, label, setting_key, hint):
        """Create a password input setting"""
        container = BoxLayout(orientation='vertical', spacing=8, size_hint_y=None, height=75)
        
        label_widget = Label(
            text=label,
            font_size=12,
            bold=True,
            color=COLORS['text_primary'],
            size_hint_y=None,
            height=25,
            halign='left'
        )
        container.add_widget(label_widget)
        
        password_input = TextInput(
            text=getattr(user_settings, setting_key) if user_settings.remember_password else '',
            hint_text=hint,
            multiline=False,
            password=True,
            size_hint_y=None,
            height=35,
            background_color=COLORS['background'],
            foreground_color=COLORS['text_primary'],
            cursor_color=COLORS['primary'],
            font_size=12,
            padding=[10, 8]
        )
        
        setattr(self, f"{setting_key}_input", password_input)
        container.add_widget(password_input)
        return container
    
    def create_switch_setting(self, label, setting_key, description):
        """Create a switch setting"""
        container = BoxLayout(orientation='horizontal', spacing=20, size_hint_y=None, height=60)
        
        info_layout = BoxLayout(orientation='vertical', spacing=4)
        
        label_widget = Label(
            text=label,
            font_size=12,
            bold=True,
            color=COLORS['text_primary'],
            halign='left',
            size_hint_y=None,
            height=25
        )
        info_layout.add_widget(label_widget)
        
        desc_widget = Label(
            text=description,
            font_size=10,
            color=COLORS['text_secondary'],
            halign='left',
            size_hint_y=None,
            height=20,
            text_size=(None, None)
        )
        info_layout.add_widget(desc_widget)
        
        container.add_widget(info_layout)
        
        switch = Switch(
            active=getattr(user_settings, setting_key),
            size_hint_x=None,
            width=70
        )
        
        setattr(self, f"{setting_key}_switch", switch)
        container.add_widget(switch)
        return container
    
    def create_button_setting(self, label, description, callback):
        """Create a button setting"""
        container = BoxLayout(orientation='horizontal', spacing=20, size_hint_y=None, height=60)
        
        info_layout = BoxLayout(orientation='vertical', spacing=4)
        
        label_widget = Label(
            text=label,
            font_size=12,
            bold=True,
            color=COLORS['text_primary'],
            halign='left',
            size_hint_y=None,
            height=25
        )
        info_layout.add_widget(label_widget)
        
        desc_widget = Label(
            text=description,
            font_size=10,
            color=COLORS['text_secondary'],
            halign='left',
            size_hint_y=None,
            height=20,
            text_size=(None, None)
        )
        info_layout.add_widget(desc_widget)
        
        container.add_widget(info_layout)
        
        button = ModernButton(
            text="Setup",
            button_type="primary",
            size_hint_x=None,
            width=100,
            height=35
        )
        button.bind(on_press=lambda x: callback())
        container.add_widget(button)
        
        return container
    
    def create_slider_setting(self, label, setting_key, min_val, max_val, step):
        """Create a slider setting"""
        container = BoxLayout(orientation='vertical', spacing=12, size_hint_y=None, height=75)
        
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=25)
        
        label_widget = Label(
            text=label,
            font_size=12,
            bold=True,
            color=COLORS['text_primary'],
            halign='left'
        )
        header_layout.add_widget(label_widget)
        
        value_label = Label(
            text=str(int(getattr(user_settings, setting_key))),
            font_size=14,
            bold=True,
            color=COLORS['primary'],
            size_hint_x=None,
            width=50,
            halign='center'
        )
        header_layout.add_widget(value_label)
        
        container.add_widget(header_layout)
        
        slider = Slider(
            min=min_val,
            max=max_val,
            value=getattr(user_settings, setting_key),
            step=step,
            size_hint_y=None,
            height=30
        )
        
        slider.bind(value=lambda instance, value: setattr(value_label, 'text', str(int(value))))
        setattr(self, f"{setting_key}_slider", slider)
        
        container.add_widget(slider)
        return container
    
    def create_folder_setting(self, label, setting_key, description):
        """Create a folder selection setting"""
        container = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height=90)
        
        label_widget = Label(
            text=label,
            font_size=12,
            bold=True,
            color=COLORS['text_primary'],
            size_hint_y=None,
            height=25,
            halign='left'
        )
        container.add_widget(label_widget)
        
        folder_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=35)
        
        folder_label = Label(
            text=getattr(user_settings, setting_key),
            font_size=10,
            color=COLORS['text_secondary'],
            halign='left',
            text_size=(None, None)
        )
        setattr(self, f"{setting_key}_label", folder_label)
        folder_layout.add_widget(folder_label)
        
        browse_btn = ModernButton(
            text="Browse",
            button_type="primary",
            size_hint_x=None,
            width=80,
            height=30
        )
        browse_btn.bind(on_press=lambda x: self.browse_folder(setting_key))
        folder_layout.add_widget(browse_btn)
        
        container.add_widget(folder_layout)
        
        desc_widget = Label(
            text=description,
            font_size=9,
            color=COLORS['text_disabled'],
            size_hint_y=None,
            height=20,
            halign='left'
        )
        container.add_widget(desc_widget)
        
        return container
    
    def browse_folder(self, setting_key):
        """Open folder browser for specific setting"""
        layout = BoxLayout(orientation='vertical', spacing=15, padding=20)
        
        title_label = Label(
            text=f"Select {setting_key.replace('_', ' ').title()}",
            font_size=16,
            bold=True,
            color=COLORS['primary'],
            size_hint_y=None,
            height=30
        )
        layout.add_widget(title_label)
        
        filechooser = FileChooserListView(
            path=getattr(user_settings, setting_key),
            dirselect=True
        )
        layout.add_widget(filechooser)
        
        button_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=40)
        
        cancel_btn = ModernButton(
            text="Cancel",
            button_type="secondary",
            size_hint=(0.5, None),
            height=35
        )
        
        select_btn = ModernButton(
            text="Select",
            button_type="success",
            size_hint=(0.5, None),
            height=35
        )
        
        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(select_btn)
        layout.add_widget(button_layout)
        
        popup = Popup(
            title="",
            content=layout,
            size_hint=(0.7, 0.6)
        )
        
        def select_folder(instance):
            if filechooser.selection:
                selected_path = filechooser.selection[0]
                folder_label = getattr(self, f"{setting_key}_label")
                folder_label.text = selected_path
                setattr(user_settings, setting_key, selected_path)
            popup.dismiss()
        
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        select_btn.bind(on_press=select_folder)
        
        popup.open()
    
    @threaded
    def setup_resources(self):
        """Setup all required resources"""
        progress_dialog = ProgressDialog("Setting up resources...")
        progress_dialog.create_popup()
        
        try:
            progress_dialog.update_progress(10, "Checking resource requirements...")
            
            success, message = ResourceManager.setup_all_resources()
            
            if success:
                progress_dialog.update_progress(100, "Resources setup complete!")
                Clock.schedule_once(lambda dt: self._show_success("Resources Setup Complete", message), 1.5)
            else:
                Clock.schedule_once(lambda dt: self._show_error("Setup Failed", message))
            
        except Exception as e:
            Clock.schedule_once(lambda dt: self._show_error("Setup Error", f"Failed to setup resources: {str(e)}"))
        finally:
            progress_dialog.close_dialog()
    
    def save_settings(self, _):
        """Save all settings"""
        if not self.username_input.text.strip():
            self._show_error("Invalid Username", "Please enter a valid Steam username.")
            return
        
        if not self.game_username_input.text.strip():
            self._show_error("Invalid Game Username", "Please enter a valid game username.")
            return
        
        user_settings.username = self.username_input.text.strip()
        user_settings.game_username = self.game_username_input.text.strip()
        user_settings.remember_password = self.remember_password_switch.active
        user_settings.auto_configure = self.auto_configure_switch.active
        user_settings.show_patch_notes = self.show_patch_notes_switch.active
        user_settings.auto_download_resources = self.auto_download_resources_switch.active
        user_settings.check_resources_on_startup = self.check_resources_on_startup_switch.active
        
        if user_settings.remember_password:
            user_settings.password = self.password_input.text.strip()
        else:
            user_settings.password = ""
        
        user_settings.max_downloads = int(self.max_downloads_slider.value)
        user_settings.auto_start_downloads = self.auto_start_downloads_switch.active
        
        if hasattr(downloader, 'MAX_DOWNLOADS'):
            downloader.MAX_DOWNLOADS = user_settings.max_downloads
        if hasattr(downloader, 'DOWNLOADS_DIR'):
            downloader.DOWNLOADS_DIR = Path(user_settings.downloads_folder)
        
        user_settings.save_settings()
        update_installation_status()
        
        self._show_success()
    
    def _show_success(self):
        """Show settings saved success message"""
        layout = BoxLayout(orientation='vertical', spacing=15, padding=20)
        
        title_label = Label(
            text="Settings Saved",
            font_size=16,
            bold=True,
            color=COLORS['accent'],
            size_hint_y=None,
            height=30
        )
        layout.add_widget(title_label)
        
        msg_label = Label(
            text="Your preferences have been updated successfully.",
            color=COLORS['text_secondary'],
            text_size=(300, None),
            halign='center',
            font_size=12
        )
        layout.add_widget(msg_label)
        
        ok_btn = ModernButton(
            text="OK",
            button_type="success",
            size_hint=(None, None),
            size=(100, 35),
            pos_hint={'center_x': 0.5}
        )
        layout.add_widget(ok_btn)
        
        popup = Popup(
            title="",
            content=layout,
            size_hint=(0.4, 0.3)
        )
        
        ok_btn.bind(on_press=lambda x: popup.dismiss())
        popup.open()
    
    def _show_error(self, title, message):
        """Show error dialog"""
        layout = BoxLayout(orientation='vertical', spacing=15, padding=20)
        
        title_label = Label(
            text=title,
            font_size=16,
            bold=True,
            color=COLORS['error'],
            size_hint_y=None,
            height=30
        )
        layout.add_widget(title_label)
        
        msg_label = Label(
            text=message,
            color=COLORS['text_primary'],
            text_size=(300, None),
            halign='center',
            font_size=12
        )
        layout.add_widget(msg_label)
        
        ok_btn = ModernButton(
            text="OK",
            button_type="danger",
            size_hint=(None, None),
            size=(100, 35),
            pos_hint={'center_x': 0.5}
        )
        layout.add_widget(ok_btn)
        
        popup = Popup(
            title="",
            content=layout,
            size_hint=(0.4, 0.3)
        )
        
        ok_btn.bind(on_press=lambda x: popup.dismiss())
        popup.open()

class ModernDownloaderApp(App):
    def build(self):
        self.title = "T's Downloader (Verges Version)"
        self.icon = None
        
        self._check_resources()
        
        sm = ScreenManager()
        sm.add_widget(LibraryScreen(name='library'))
        sm.add_widget(SettingsScreen(name='settings'))
        
        return sm

    @threaded
    def _check_resources(self):
        """Background resource checking"""
        try:
            if user_settings.check_resources_on_startup:
                success, missing = ResourceManager.check_resources()
                
                if not success and user_settings.auto_download_resources:
                    print("Missing resources detected, setting up automatically...")
                    ResourceManager.setup_all_resources()
            
            if hasattr(downloader, 'check_onedrive'):
                downloader.check_onedrive()
            if hasattr(downloader, 'ensure_dotnet'):
                downloader.ensure_dotnet()
            if hasattr(downloader, 'ensure_resources'):
                downloader.ensure_resources()
            
            if hasattr(downloader, 'MAX_DOWNLOADS'):
                downloader.MAX_DOWNLOADS = user_settings.max_downloads
            if hasattr(downloader, 'DOWNLOADS_DIR'):
                downloader.DOWNLOADS_DIR = Path(user_settings.downloads_folder)
            
        except Exception as e:
            def show_startup_error(dt):
                layout = BoxLayout(orientation='vertical', spacing=20, padding=25)
                
                title_label = Label(
                    text="STARTUP WARNING",
                    font_size=18,
                    bold=True,
                    color=COLORS['warning'],
                    size_hint_y=None,
                    height=30
                )
                layout.add_widget(title_label)
                
                error_label = Label(
                    text=f"Some initialization steps failed:\n\n{str(e)}\n\nThe application will continue, but some features may not work correctly.",
                    color=COLORS['text_primary'],
                    text_size=(450, None),
                    halign='center',
                    font_size=12
                )
                layout.add_widget(error_label)
                
                continue_btn = ModernButton(
                    text="Continue",
                    button_type="warning",
                    size_hint=(None, None),
                    size=(120, 35),
                    pos_hint={'center_x': 0.5}
                )
                layout.add_widget(continue_btn)
                
                popup = Popup(
                    title="",
                    content=layout,
                    size_hint=(0.6, 0.5),
                    auto_dismiss=False
                )
                
                continue_btn.bind(on_press=lambda x: popup.dismiss())
                popup.open()
            
            Clock.schedule_once(show_startup_error, 1)

    def on_start(self):
        """Called when the app starts"""
        update_installation_status()
        
        if not user_settings.username:
            def show_welcome(dt):
                layout = BoxLayout(orientation='vertical', spacing=25, padding=30)
                
                title_label = Label(
                    text="Welcome to T's Downloader (Verges Version)",
                    font_size=20,
                    bold=True,
                    color=COLORS['text_primary'],
                    size_hint_y=None,
                    height=35
                )
                layout.add_widget(title_label)
                
                welcome_text = Label(
                    text="Hope you have a better experience using T's Downloader\n\nDownload and play legacy versions, test servers, and manage your installations with ease.\n\nConfigure your Steam credentials in Settings to get started.",
                    color=COLORS['text_secondary'],
                    text_size=(500, None),
                    halign='center',
                    font_size=12
                )
                layout.add_widget(welcome_text)
                
                button_layout = BoxLayout(orientation='horizontal', spacing=20, size_hint_y=None, height=50)
                
                settings_btn = ModernButton(
                    text="Open Settings",
                    button_type="primary",
                    size_hint=(0.5, None),
                    height=40
                )
                
                browse_btn = ModernButton(
                    text="Browse Library",
                    button_type="secondary",
                    size_hint=(0.5, None),
                    height=40
                )
                
                button_layout.add_widget(settings_btn)
                button_layout.add_widget(browse_btn)
                layout.add_widget(button_layout)
                
                popup = Popup(
                    title="",
                    content=layout,
                    size_hint=(0.7, 0.6),
                    auto_dismiss=False
                )
                
                settings_btn.bind(on_press=lambda x: [popup.dismiss(), setattr(self.root, 'current', 'settings')])
                browse_btn.bind(on_press=lambda x: popup.dismiss())
                
                popup.open()
            
            Clock.schedule_once(show_welcome, 1.0)

if __name__ == '__main__':
    try:
        ModernDownloaderApp().run()
    except Exception as e:
        print(f"Application crashed: {e}")
        input("Press Enter to exit...")