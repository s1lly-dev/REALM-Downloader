use eframe::egui;
use std::collections::HashMap;
use std::path::PathBuf;
use std::process::{Command, Stdio};
use std::sync::{Arc, Mutex};
use std::thread;
use std::io::{BufRead, BufReader};

#[derive(Debug, Clone)]
struct SeasonInfo {
    name: String,
    year: String,
    size: String,
    notes: String,
    manifests: Vec<(u32, String)>,
    crack_folder: String,
}

#[derive(Debug, Clone, PartialEq)]
enum AppState {
    MainMenu,
    GameDownloader,
    TestServers,
    FourKTextures,
    ExtraTools,
    Settings,
    Guide,
    Downloading,
}

#[derive(Debug, Clone, PartialEq)]
enum DownloadStatus {
    NotStarted,
    InProgress,
    Completed,
    Failed(String),
}

struct RealmDownloaderApp {
    state: AppState,
    username: String,
    password: String,
    show_password: bool,
    seasons: HashMap<String, SeasonInfo>,
    test_servers: HashMap<String, SeasonInfo>,
    four_k_textures: HashMap<String, (String, String)>, 
    selected_season: Option<String>,
    download_status: DownloadStatus,
    download_progress: f32,
    max_downloads: u32,
    downloads_folder: PathBuf,
    download_handle: Option<Arc<Mutex<bool>>>,
    download_output: Arc<Mutex<Vec<String>>>,
    download_status_handle: Arc<Mutex<DownloadStatus>>,
    username_error: String,
    resources_ready: Arc<Mutex<bool>>,
}

impl Default for RealmDownloaderApp {
    fn default() -> Self {
        let resources_ready = Arc::new(Mutex::new(false));
        
        let mut app = Self {
            state: AppState::MainMenu,
            username: String::new(),
            password: String::new(),
            show_password: false,
            seasons: HashMap::new(),
            test_servers: HashMap::new(),
            four_k_textures: HashMap::new(),
            selected_season: None,
            download_status: DownloadStatus::NotStarted,
            download_progress: 0.0,
            max_downloads: 25,
            downloads_folder: PathBuf::from("Downloads"),
            download_handle: None,
            download_output: Arc::new(Mutex::new(Vec::new())),
            download_status_handle: Arc::new(Mutex::new(DownloadStatus::NotStarted)),
            username_error: String::new(),
            resources_ready: Arc::clone(&resources_ready),
        };
        
        app.initialize_seasons();
        app.initialize_test_servers();
        app.initialize_4k_textures();
        
        let resources_ready_clone = Arc::clone(&resources_ready);
        thread::spawn(move || {
            RealmDownloaderApp::ensure_resources_exist();
                        let mut ready = resources_ready_clone.lock().unwrap();
            *ready = true;
        });
        
        app
    }
}

// Need to add the actual game sizes if they are in accurate
impl RealmDownloaderApp {
    fn initialize_seasons(&mut self) {
        let seasons_data = vec![
            ("Prep Phase", "Y10S1", "51.4 GB", "NO UNLOCKED OPERATORS", 
             vec![(377237, "8382986432868135995"), (377238, "3364322644809414267"), (359551, "2619322944995294928")], 
             "Y6S4-Y8SX"),
            ("Collision Point", "Y9S4", "59.2 GB", "NO UNLOCKED OPERATORS", 
             vec![(377237, "9207916394092784817"), (377238, "6303744364362141965"), (359551, "3039751959139581613")], 
             "Y6S4-Y8SX"),
            ("Twin Shells", "Y9S3", "59.2 GB", "NO UNLOCKED OPERATORS", 
             vec![(377237, "4296569502001540403"), (377238, "3038245830342960035"), (359551, "825321500774263546")], 
             "Y6S4-Y8SX"),
            ("New Blood", "Y9S2", "xx.x GB", "NO UNLOCKED OPERATORS", 
             vec![(377237, "8160812118480939262"), (377238, "2207285510020603118"), (359551, "3303120421075579181")], 
             "Y6S4-Y8SX"),
            ("Deadly Omen", "Y9S1", "xx.x GB", "NO UNLOCKED OPERATORS", 
             vec![(377237, "1959067516419454682"), (377238, "1619182300337183882"), (359551, "1140469899661941149")], 
             "Y6S4-Y8SX"),
            ("Deep Freeze", "Y8S4", "52.9 GB", "NO UNLOCKED OPERATORS", 
             vec![(377237, "7646647065987620875"), (377238, "8339919149418587132"), (359551, "4957295777170965935")], 
             "Y6S4-Y8SX"),
            ("Heavy Mettle", "Y8S3", "xx.x GB", "NO UNLOCKED OPERATORS", 
             vec![(377237, "2068160275622519212"), (377238, "2579928666708989224"), (359551, "3005637025719884427")], 
             "Y6S4-Y8SX"),
            ("Dread Factor", "Y8S2", "xx.x GB", "", 
             vec![(377237, "3050554908913191669"), (377238, "4293396692730784956"), (359551, "1575870740329742681")], 
             "Y6S4-Y8SX"),
            ("Commanding Force", "Y8S1", "xx.x GB", "", 
             vec![(377237, "3275824905781062648"), (377238, "1252692309389076318"), (359551, "5863062164463920572")], 
             "Y6S4-Y8SX"),
            ("Solar Raid", "Y7S4", "xx.x GB", "", 
             vec![(377237, "4466027729495813039"), (377238, "5107849703917033235"), (359551, "1819898955518120444")], 
             "Y6S4-Y8SX"),
            ("Brutal Swarm", "Y7S3", "xx.x GB", "", 
             vec![(377237, "6425223567680952075"), (377238, "4623590620762156001"), (359551, "5906302942203575464")], 
             "Y6S4-Y8SX"),
            ("Vector Glare", "Y7S2", "xx.x GB", "", 
             vec![(377237, "1363132201391540345"), (377238, "4500117484519539380"), (359551, "133280937611742404")], 
             "Y6S4-Y8SX"),
            ("Demon Veil", "Y7S1", "xx.x GB", "", 
             vec![(377237, "8323869632165751287"), (377238, "1970003626423861715"), (359551, "2178080523228113690")], 
             "Y6S4-Y8SX"),
            ("High Calibre", "Y6S4", "xx.x GB", "", 
             vec![(377237, "2637055726475611418"), (377238, "2074678920289758165"), (359551, "8627214406801860013")], 
             "Y6S4-Y8SX"),
            ("Crystal Guard", "Y6S3", "xx.x GB", "", 
             vec![(377237, "4859695099882698284"), (377238, "5161489294178683219"), (359551, "6526531850721822265")], 
             "Y6S3"),
            ("North Star", "Y6S2", "xx.x GB", "", 
             vec![(377237, "8733653062998518164"), (377238, "6767916709017546201"), (359551, "809542866761090243")], 
             "Y1SX-Y6S2"),
            ("Crimson Heist", "Y6S1", "xx.x GB", "", 
             vec![(377237, "7890853311380514304"), (377238, "6130917224459224462"), (359551, "7485515457663576274")], 
             "Y1SX-Y6S2"),
            ("Neon Dawn", "Y5S4", "xx.x GB", "Road To S.I. 2021", 
             vec![(377237, "4713320084981112320"), (377238, "3560446343418579092"), (359551, "3711873929777458413")], 
             "Y1SX-Y6S2"),
            ("Neon Dawn (HM)", "Y5S4", "xx.x GB", "SUPPORTS HEATED METAL", 
             vec![(377237, "3390446325154338855"), (377238, "3175150742361965235"), (359551, "6947060999143280245")], 
             "Y1SX-Y6S2"),
            ("Shadow Legacy", "Y5S3", "88.0 GB", "", 
             vec![(377237, "85893637567200342"), (377238, "4020038723910014041"), (359551, "3089981610366186823")], 
             "Y1SX-Y6S2"),
            ("Steel Wave", "Y5S2", "81.3 GB", "", 
             vec![(377237, "4367817844736324940"), (377238, "5838065097101371940"), (359551, "893971391196952070")], 
             "Y1SX-Y6S2"),
            ("Void Edge", "Y5S1", "74.3 GB", "", 
             vec![(377237, "4736360397583523381"), (377238, "2583838033617047180"), (359551, "6296533808765702678")], 
             "Y1SX-Y6S2"),
            ("Shifting Tides", "Y4S4", "75.2 GB", "", 
             vec![(377237, "299124516841461614"), (377238, "510172308722680354"), (359551, "1842268638395240106")], 
             "Y1SX-Y6S2"),
            ("Ember Rise", "Y4S3", "69.6 GB", "Doktor's Curse + Money Heist Event", 
             vec![(377237, "3546781236735558235"), (377238, "684480090862996679"), (359551, "7869081741739849703")], 
             "Y1SX-Y6S2"),
            ("Phantom Sight", "Y4S2", "67.1 GB", "Showdown Event", 
             vec![(377237, "693082837425613508"), (377238, "3326664059403997209"), (359551, "5408324128694463720")], 
             "Y1SX-Y6S2"),
            ("Burnt Horizon", "Y4S1", "59.7 GB", "Rainbow Is Magic Event", 
             vec![(377237, "8356277316976403078"), (377238, "3777349673527123995"), (359551, "5935578581006804383")], 
             "Y1SX-Y6S2"),
            ("Wind Bastion", "Y3S4", "76.9 GB", "", 
             vec![(377237, "6502258854032233436"), (377238, "3144556314994867170"), (359551, "7659555540733025386")], 
             "Y1SX-Y6S2"),
            ("Grim Sky", "Y3S3", "72.6 GB", "Mad House Event", 
             vec![(377237, "5562094852451837435"), (377238, "3144556314994867170"), (359551, "7781202564071310413")], 
             "Y1SX-Y6S2"),
            ("Para Bellum", "Y3S2", "63.3 GB", "", 
             vec![(377237, "6507886921175556869"), (377238, "7995779530685147208"), (359551, "8765715607275074515")], 
             "Y1SX-Y6S2"),
            ("Chimera", "Y3S1", "58.8 GB", "Outbreak Event", 
             vec![(377237, "5071357104726974256"), (377238, "4768963659370299631"), (359551, "4701787239566783972")], 
             "Y1SX-Y6S2"),
            ("White Noise", "Y2S4", "48.7 GB", "", 
             vec![(377237, "8748734086032257441"), (377238, "8421028160473337894"), (359551, "4221297486420648079")], 
             "Y1SX-Y6S2"),
            ("Blood Orchid", "Y2S3", "34.3 GB", "", 
             vec![(377237, "6708129824495912434"), (377238, "4662662335520989204"), (359551, "1613631671988840841")], 
             "Y1SX-Y6S2"),
            ("Health", "Y2S2", "34.0 GB", "", 
             vec![(377237, "5875987479498297665"), (377238, "8542242518901049325"), (359551, "708773000306432190")], 
             "Y1SX-Y6S2"),
            ("Velvet Shell", "Y2S1", "33.2 GB", "", 
             vec![(377237, "2248734317261478192"), (377238, "2687181326074258760"), (359551, "8006071763917433748")], 
             "Y1SX-Y6S2"),
            ("Red Crow", "Y1S4", "28.5 GB", "", 
             vec![(377237, "3576607363557872807"), (377238, "912564683190696342"), (359551, "8569920171217002292")], 
             "Y1SX-Y6S2"),
            ("Skull Rain", "Y1S3", "25.1 GB", "", 
             vec![(377237, "5819137024728546741"), (377238, "2956768406107766016"), (359551, "5851804596427790505")], 
             "Y1SX-Y6S2"),
            ("Dust Line", "Y1S2", "20.9 GB", "", 
             vec![(377237, "2303064029242396590"), (377238, "3040224537841664111"), (359551, "2206497318678061176")], 
             "Y1SX-Y6S2"),
            ("Black Ice", "Y1S1", "16.7 GB", "", 
             vec![(377237, "5188997148801516344"), (377238, "5362991837480196824"), (359551, "7932785808040895147")], 
             "Y1SX-Y6S2"),
            ("Vanilla", "Y1S0", "14.2 GB", "", 
             vec![(377237, "8358812283631269928"), (377238, "6835384933146381100"), (359551, "3893422760579204530")], 
             "Y1SX-Y6S2"),
        ];

        for (name, year, size, notes, manifests, crack_folder) in seasons_data {
            self.seasons.insert(
                name.to_string(),
                SeasonInfo {
                    name: name.to_string(),
                    year: year.to_string(),
                    size: size.to_string(),
                    notes: notes.to_string(),
                    manifests: manifests.into_iter().map(|(depot, manifest)| (depot, manifest.to_string())).collect(),
                    crack_folder: crack_folder.to_string(),
                },
            );
        }
    }
      // Likley to remove later in the release (:
    fn initialize_test_servers(&mut self) {
        let test_server_data = vec![
            ("Daybreak TS", "Y10S2", "28/05/25", 
             vec![(623991, "5235883268902565724")], "Y6S4-Y8SX"),
            ("North Star TS", "Y6S2", "25/05/21", 
             vec![(623991, "6881719580573646381")], "Y1SX-Y6S2"),
            ("Crimson Heist TS", "Y6S1", "22/02/21", 
             vec![(623991, "7921295012062018715")], "Y1SX-Y6S2"),
            ("Ember Rise TS", "Y4S3", "10/09/19", 
             vec![(623991, "8284402568137361637")], "Y1SX-Y6S2"),
            ("Shadow Legacy TS", "Y5S3", "08/10/20", 
             vec![(623991, "8833805637802398440")], "Y1SX-Y6S2"),
            ("Steel Wave TS", "Y5S2", "02/06/20", 
             vec![(623991, "1268848856509013057")], "Y1SX-Y6S2"),
        ];

        for (name, year, date, manifests, crack_folder) in test_server_data {
            self.test_servers.insert(
                name.to_string(),
                SeasonInfo {
                    name: name.to_string(),
                    year: year.to_string(),
                    size: date.to_string(),
                    notes: String::new(),
                    manifests: manifests.into_iter().map(|(depot, manifest)| (depot, manifest.to_string())).collect(),
                    crack_folder: crack_folder.to_string(),
                },
            );
        }
    }

    fn initialize_4k_textures(&mut self) {
        let texture_data = vec![
            ("Vanilla", "Y1S0", "8394183851197739981"),
            ("Black Ice", "Y1S1", "3756048967966286899"),
            ("Dust Line", "Y1S2", "1338949402410764888"),
            ("Skull Rain", "Y1S3", "3267970968757091405"),
            ("Red Crow", "Y1S4", "1825939060444887403"),
            ("Velvet Shell", "Y2S1", "3196596628759979362"),
            ("Health", "Y2S2", "7497579858536910279"),
            ("Blood Orchid", "Y2S3", "6420469519659049757"),
            ("White Noise", "Y2S4", "1118649577165385479"),
            ("Chimera", "Y3S1", "1668513364192382097"),
            ("Para Bellum", "Y3S2", "204186978012641075"),
            ("Grim Sky", "Y3S3", "6431001239225997495"),
            ("Wind Bastion", "Y3S4", "2243348760021617592"),
            ("Burnt Horizon", "Y4S1", "3462709886432904855"),
            ("Phantom Sight", "Y4S2", "4107080515154236795"),
            ("Ember Rise", "Y4S3", "8340682081776225833"),
            ("Shifting Tides", "Y4S4", "6048763664997452513"),
            ("Void Edge", "Y5S1", "2194493692563107142"),
            ("Steel Wave", "Y5S2", "3257522596542046976"),
        ];

        for (name, year, manifest) in texture_data {
            self.four_k_textures.insert(name.to_string(), (year.to_string(), manifest.to_string()));
        }
    }
     // Basically get and download the resources and BS 
    fn ensure_resources_exist() {
        let resources_dir = std::env::current_dir().unwrap_or_default().join("Resources");
        let tools_dir = resources_dir.join("Tools");
        
        if let Err(e) = std::fs::create_dir_all(&tools_dir) {
            eprintln!("Failed to create Resources/Tools directory: {}", e);
            return;
        }

        let seven_zip_path = resources_dir.join("7z.exe");
        if !seven_zip_path.exists() {
            println!("Downloading 7-Zip...");
            Self::download_file(
                "https://github.com/DataCluster0/R6TBBatchTool/raw/master/Requirements/7z.exe",
                &seven_zip_path
            );
        }

        let depot_downloader_path = resources_dir.join("DepotDownloader.dll");
        if !depot_downloader_path.exists() {
            println!("Downloading DepotDownloader...");
            let depot_zip_path = resources_dir.join("depot.zip");
            
            if Self::download_file(
                "https://github.com/SteamRE/DepotDownloader/releases/download/DepotDownloader_3.4.0/DepotDownloader-framework.zip",
                &depot_zip_path
            ) {
                if seven_zip_path.exists() {
                    let _ = Command::new(&seven_zip_path)
                        .args(&["x", "-y", depot_zip_path.to_str().unwrap_or(""), &format!("-o{}", resources_dir.to_str().unwrap_or("")), "-aoa"])
                        .status();
                } else {
                    Self::extract_zip(&depot_zip_path, &resources_dir);
                }
                let _ = std::fs::remove_file(&depot_zip_path);
            }
        }

        let cracks_dir = resources_dir.join("Cracks");
        if !cracks_dir.exists() {
            println!("Downloading Cracks...");
            let cracks_zip_path = resources_dir.join("Cracks.zip");
            
            if Self::download_file(
                "https://github.com/Vergepoland/r6-downloader/raw/refs/heads/main/Cracks.zip",
                &cracks_zip_path
            ) {
                if seven_zip_path.exists() {
                    let _ = Command::new(&seven_zip_path)
                        .args(&["x", "-y", cracks_zip_path.to_str().unwrap_or(""), &format!("-o{}", cracks_dir.to_str().unwrap_or("")), "-aoa"])
                        .status();
                } else {
                    Self::extract_zip(&cracks_zip_path, &cracks_dir);
                }
                let _ = std::fs::remove_file(&cracks_zip_path);
            }
        }

        let localization_path = resources_dir.join("localization.lang");
        if !localization_path.exists() {
            println!("Downloading localization file...");
            Self::download_file(
                "https://github.com/Vergepoland/r6-downloader/raw/refs/heads/main/localization.lang",
                &localization_path
            );
        }

        println!("Resource check complete!");
    }

    fn download_file(url: &str, output_path: &std::path::Path) -> bool {
        let mut cmd = Command::new("curl");
        cmd.args(&[
            "-L", url,
            "--ssl-no-revoke",
            "--output", output_path.to_str().unwrap_or(""),
        ]);

        match cmd.status() {
            Ok(status) => {
                if status.success() {
                    println!("Successfully downloaded: {}", output_path.file_name().unwrap_or_default().to_string_lossy());
                    true
                } else {
                    eprintln!("Failed to download: {}", url);
                    false
                }
            }
            Err(e) => {
                eprintln!("Failed to execute download command: {}", e);
                false
            }
        }
    }

    fn extract_zip(zip_path: &std::path::Path, extract_to: &std::path::Path) {
        if cfg!(windows) {
            let ps_command = format!(
                "Expand-Archive -Path '{}' -DestinationPath '{}' -Force",
                zip_path.display(),
                extract_to.display()
            );
            let _ = Command::new("powershell")
                .args(&["-Command", &ps_command])
                .status();
        } else {
            let _ = Command::new("unzip")
                .args(&["-o", zip_path.to_str().unwrap_or(""), "-d", extract_to.to_str().unwrap_or("")])
                .status();
        }
    }

    fn start_download(&mut self, season_key: &str, is_test_server: bool) {
        self.username_error.clear();
        
        if self.username.trim().is_empty() {
            self.username_error = "Username is required".to_string();
            return;
        }

        let season_info = if is_test_server {
            self.test_servers.get(season_key).cloned()
        } else {
            self.seasons.get(season_key).cloned()
        };

        if let Some(season) = season_info {
            self.download_status = DownloadStatus::InProgress;
            self.download_progress = 0.0;
            self.state = AppState::Downloading;
            
            {
                let mut shared_status = self.download_status_handle.lock().unwrap();
                *shared_status = DownloadStatus::InProgress;
            }
            
            {
                let mut output = self.download_output.lock().unwrap();
                output.clear();
                output.push(format!("Starting download of {}...", season.name));
            }

            let username = self.username.clone();
            let password = self.password.clone();
            let downloads_folder = self.downloads_folder.clone();
            let max_downloads = self.max_downloads;
            let app_id = if is_test_server { 623990 } else { 359550 };
            let output_handle = Arc::clone(&self.download_output);
            let status_handle = Arc::clone(&self.download_status_handle);
            
            let cancel_handle = Arc::new(Mutex::new(false));
            self.download_handle = Some(cancel_handle.clone());
            
            thread::spawn(move || {
                let final_status = Self::execute_download(
                    username,
                    password,
                    season,
                    downloads_folder,
                    max_downloads,
                    app_id,
                    cancel_handle,
                    output_handle,
                );
                
                let mut status = status_handle.lock().unwrap();
                *status = final_status;
            });
        }
    }

    fn start_4k_download(&mut self, season_key: &str) {
        self.username_error.clear();
        
        if self.username.trim().is_empty() {
            self.username_error = "Username is required".to_string();
            return;
        }

        if let Some((year, manifest)) = self.four_k_textures.get(season_key).cloned() {
            let season_info = SeasonInfo {
                name: format!("{} 4K Textures", season_key),
                year: year.clone(),
                size: "4K Textures".to_string(),
                notes: "High Resolution Textures".to_string(),
                manifests: vec![(377239, manifest)],
                crack_folder: String::new(),
            };

            self.download_status = DownloadStatus::InProgress;
            self.download_progress = 0.0;
            self.state = AppState::Downloading;
            
            {
                let mut shared_status = self.download_status_handle.lock().unwrap();
                *shared_status = DownloadStatus::InProgress;
            }
            
            {
                let mut output = self.download_output.lock().unwrap();
                output.clear();
                output.push(format!("Starting 4K texture download for {}...", season_key));
            }

            let username = self.username.clone();
            let password = self.password.clone();
            let downloads_folder = self.downloads_folder.clone();
            let max_downloads = self.max_downloads;
            let output_handle = Arc::clone(&self.download_output);
            let status_handle = Arc::clone(&self.download_status_handle);
            
            let cancel_handle = Arc::new(Mutex::new(false));
            self.download_handle = Some(cancel_handle.clone());
            
            thread::spawn(move || {
                let final_status = Self::execute_download(
                    username,
                    password,
                    season_info,
                    downloads_folder,
                    max_downloads,
                    359550,
                    cancel_handle,
                    output_handle,
                );
                
                let mut status = status_handle.lock().unwrap();
                *status = final_status;
            });
        }
    }

    fn execute_download(
        username: String,
        password: String,
        season: SeasonInfo,
        downloads_folder: PathBuf,
        max_downloads: u32,
        app_id: u32,
        cancel_handle: Arc<Mutex<bool>>,
        output_handle: Arc<Mutex<Vec<String>>>,
    ) -> DownloadStatus {
        let season_folder = downloads_folder.join(&format!("{}_{}", season.year, season.name.replace(" ", "")));
        
        if let Err(e) = std::fs::create_dir_all(&season_folder) {
            let error_msg = format!("Failed to create download directory: {}", e);
            let mut output = output_handle.lock().unwrap();
            output.push(error_msg.clone());
            return DownloadStatus::Failed(error_msg);
        }

        for (depot_id, manifest_id) in &season.manifests {
            if *cancel_handle.lock().unwrap() {
                let mut output = output_handle.lock().unwrap();
                output.push("Download cancelled by user".to_string());
                return DownloadStatus::Failed("Download cancelled by user".to_string());
            }

            {
                let mut output = output_handle.lock().unwrap();
                output.push(format!("Downloading depot {} with manifest {}...", depot_id, manifest_id));
            }

            let depot_downloader_path = std::env::current_dir()
                .unwrap_or_default()
                .join("Resources")
                .join("DepotDownloader.dll");
            
            if !depot_downloader_path.exists() {
                let error_msg = format!("DepotDownloader.dll not found at: {}", depot_downloader_path.display());
                let mut output = output_handle.lock().unwrap();
                output.push(error_msg.clone());
                return DownloadStatus::Failed(error_msg);
            }

            let mut cmd = Command::new("dotnet");
            cmd.args(&[
                depot_downloader_path.to_str().unwrap_or(""),
                "-app", &app_id.to_string(),
                "-depot", &depot_id.to_string(),
                "-manifest", manifest_id,
                "-username", &username,
                "-remember-password",
                "-dir", season_folder.to_str().unwrap_or(""),
                "-validate",
                "-max-downloads", &max_downloads.to_string(),
            ]);

            if !password.is_empty() {
                cmd.arg("-password").arg(&password);
            }

            cmd.stdout(Stdio::piped()).stderr(Stdio::piped());

            match cmd.spawn() {
                Ok(mut child) => {
                    if let Some(stdout) = child.stdout.take() {
                        let reader = BufReader::new(stdout);
                        for line in reader.lines() {
                            if let Ok(line) = line {
                                let mut output = output_handle.lock().unwrap();
                                output.push(line);
                                if output.len() > 1000 {
                                    output.remove(0);
                                }
                            }
                        }
                    }

                    match child.wait() {
                        Ok(status) => {
                            if !status.success() {
                                let error_msg = format!("Download failed for depot {} (exit code: {})", depot_id, status.code().unwrap_or(-1));
                                let mut output = output_handle.lock().unwrap();
                                output.push(error_msg.clone());
                                return DownloadStatus::Failed(error_msg);
                            } else {
                                let mut output = output_handle.lock().unwrap();
                                output.push(format!("Successfully downloaded depot {}", depot_id));
                            }
                        }
                        Err(e) => {
                            let error_msg = format!("Failed to wait for download process: {}", e);
                            let mut output = output_handle.lock().unwrap();
                            output.push(error_msg.clone());
                            return DownloadStatus::Failed(error_msg);
                        }
                    }
                }
                Err(e) => {
                    let error_msg = format!("Failed to start download process: {}", e);
                    let mut output = output_handle.lock().unwrap();
                    output.push(error_msg.clone());
                    return DownloadStatus::Failed(error_msg);
                }
            }
        }

        if !season.crack_folder.is_empty() {
            {
                let mut output = output_handle.lock().unwrap();
                output.push("Copying crack files and localization...".to_string());
            }

            let resources_folder = std::env::current_dir().unwrap_or_default().join("Resources");
            let crack_source = resources_folder.join("Cracks").join(&season.crack_folder);
            let localization_source = resources_folder.join("localization.lang");

            if crack_source.exists() {
                if let Err(e) = copy_dir_all(&crack_source, &season_folder) {
                    let mut output = output_handle.lock().unwrap();
                    output.push(format!("Failed to copy crack files: {}", e));
                } else {
                    let mut output = output_handle.lock().unwrap();
                    output.push("Crack files copied successfully".to_string());
                }
            }

            if localization_source.exists() {
                let localization_dest = season_folder.join("localization.lang");
                if let Err(e) = std::fs::copy(&localization_source, &localization_dest) {
                    let mut output = output_handle.lock().unwrap();
                    output.push(format!("Failed to copy localization file: {}", e));
                } else {
                    let mut output = output_handle.lock().unwrap();
                    output.push("Localization file copied successfully".to_string());
                }
            }
        }

        {
            let mut output = output_handle.lock().unwrap();
            output.push(format!("Download completed successfully for {}", season.name));
            if season.name.contains("4K") {
                output.push("4K textures are now available in your game directory".to_string());
            } else {
                output.push("You can now launch the game using RainbowSix.bat".to_string());
            }
        }

        DownloadStatus::Completed
    }

    fn cancel_download(&mut self) {
        if let Some(handle) = &self.download_handle {
            let mut should_cancel = handle.lock().unwrap();
            *should_cancel = true;
        }
        self.download_status = DownloadStatus::NotStarted;
        self.download_progress = 0.0;
        self.state = AppState::MainMenu;
        self.download_handle = None;
    }

    fn download_tool(&self, url: &str, filename: &str) {
        let url = url.to_string();
        let filename = filename.to_string();
        let tools_folder = std::env::current_dir().unwrap_or_default().join("Resources").join("Tools");
        
        thread::spawn(move || {
            if let Err(e) = std::fs::create_dir_all(&tools_folder) {
                eprintln!("Failed to create tools directory: {}", e);
                return;
            }
            
            let output_path = tools_folder.join(&filename);
            let mut cmd = Command::new("curl");
            cmd.args(&[
                "-L", &url,
                "--ssl-no-revoke",
                "--output", output_path.to_str().unwrap_or(""),
            ]);
            
            match cmd.status() {
                Ok(status) => {
                    if status.success() {
                        println!("Successfully downloaded {}", filename);
                        
                        if filename.ends_with(".zip") || filename.ends_with(".7z") {
                            let seven_zip_path = std::env::current_dir().unwrap_or_default().join("Resources").join("7z.exe");
                            
                            if seven_zip_path.exists() {
                                let _ = Command::new(&seven_zip_path)
                                    .args(&["x", "-y", output_path.to_str().unwrap_or(""), &format!("-o{}", tools_folder.to_str().unwrap_or("")), "-aoa"])
                                    .status();
                                let _ = std::fs::remove_file(&output_path);
                                println!("Successfully extracted {}", filename);
                            } else if cfg!(windows) {
                                let ps_command = format!(
                                    "Expand-Archive -Path '{}' -DestinationPath '{}' -Force",
                                    output_path.display(),
                                    tools_folder.display()
                                );
                                let _ = Command::new("powershell")
                                    .args(&["-Command", &ps_command])
                                    .status();
                                let _ = std::fs::remove_file(&output_path);
                            }
                        }
                    } else {
                        eprintln!("Failed to download {}", filename);
                    }
                }
                Err(e) => {
                    eprintln!("Failed to execute download command: {}", e);
                }
            }
        });
    }
}

impl eframe::App for RealmDownloaderApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        if self.download_status == DownloadStatus::InProgress {
            let shared_status = self.download_status_handle.lock().unwrap();
            if *shared_status != DownloadStatus::InProgress {
                self.download_status = shared_status.clone();
            }
        }
        
        egui::CentralPanel::default().show(ctx, |ui| {
            match self.state {
                AppState::MainMenu => self.show_main_menu(ui),
                AppState::GameDownloader => self.show_game_downloader(ui),
                AppState::TestServers => self.show_test_servers(ui),
                AppState::FourKTextures => self.show_4k_textures(ui),
                AppState::ExtraTools => self.show_extra_tools(ui),
                AppState::Settings => self.show_settings(ui),
                AppState::Guide => self.show_guide(ui),
                AppState::Downloading => self.show_downloading(ui),
            }
        });
        
        ctx.request_repaint();
    }
}

impl RealmDownloaderApp {
    fn show_main_menu(&mut self, ui: &mut egui::Ui) {
        ui.vertical_centered(|ui| {
            ui.add_space(20.0);
            ui.heading("REALM");
            ui.add_space(10.0);
            ui.label("Old R6:S Downloader");
            ui.add_space(20.0);
            
            let resources_ready = *self.resources_ready.lock().unwrap();
            
            if !resources_ready {
                ui.label("Setting up required files...");
                ui.add_space(10.0);
                ui.spinner();
                ui.add_space(20.0);
                return;
            }
            
            ui.label("WARNING: YOU MUST CLAIM A FREE COPY OF SIEGE ON STEAM TO USE THE DOWNLOADER");
            ui.add_space(20.0);

            let button_size = egui::vec2(300.0, 40.0);
            
            if ui.add_sized(button_size, egui::Button::new("Game Downloader")).clicked() {
                self.state = AppState::GameDownloader;
            }
            ui.add_space(10.0);
            
            if ui.add_sized(button_size, egui::Button::new("Test Server Downloader")).clicked() {
                self.state = AppState::TestServers;
            }
            ui.add_space(10.0);
            
            if ui.add_sized(button_size, egui::Button::new("4K Textures Download")).clicked() {
                self.state = AppState::FourKTextures;
            }
            ui.add_space(10.0);
            
            if ui.add_sized(button_size, egui::Button::new("Extra Tools")).clicked() {
                self.state = AppState::ExtraTools;
            }
            ui.add_space(10.0);
            
            if ui.add_sized(button_size, egui::Button::new("Claim Siege on Steam")).clicked() {
                if let Err(e) = webbrowser::open("https://store.steampowered.com/app/359550/Tom_Clancys_Rainbow_Six_Siege_X/") {
                    eprintln!("Failed to open browser: {}", e);
                }
            }
            ui.add_space(10.0);
            
            if ui.add_sized(button_size, egui::Button::new("Settings")).clicked() {
                self.state = AppState::Settings;
            }
            ui.add_space(10.0);
            
            if ui.add_sized(button_size, egui::Button::new("Installation Guide and FAQ")).clicked() {
                self.state = AppState::Guide;
            }
        });
    }

    fn show_game_downloader(&mut self, ui: &mut egui::Ui) {
        let mut back_clicked = false;
        let mut selected_season_key: Option<String> = None;
        
        ui.vertical(|ui| {
            ui.horizontal(|ui| {
                if ui.button("← Back to Main Menu").clicked() {
                    back_clicked = true;
                }
                ui.separator();
                ui.heading("Game Downloader");
            });
            
            ui.add_space(10.0);
            
            ui.horizontal(|ui| {
                ui.label("Steam Username:");
                let response = ui.text_edit_singleline(&mut self.username);
                if response.changed() {
                    self.username_error.clear();
                }
            });
            
            if !self.username_error.is_empty() {
                ui.colored_label(egui::Color32::RED, &self.username_error);
            }
            
            ui.horizontal(|ui| {
                ui.label("Steam Password:");
                if self.show_password {
                    ui.text_edit_singleline(&mut self.password);
                } else {
                    ui.add(egui::TextEdit::singleline(&mut self.password).password(true));
                }
                ui.checkbox(&mut self.show_password, "Show");
            });
            
            ui.add_space(10.0);
            ui.separator();
            ui.add_space(10.0);
            
            ui.label("Select a Rainbow Six Siege version to download:");
            
            egui::ScrollArea::vertical().show(ui, |ui| {
                let mut seasons: Vec<_> = self.seasons.iter().collect();
                seasons.sort_by(|a, b| b.1.year.cmp(&a.1.year));
                
                for (season_key, season_info) in seasons {
                    ui.horizontal(|ui| {
                        let button_text = format!("{} | {} | {}", season_info.name, season_info.year, season_info.size);
                        if ui.button(button_text).clicked() {
                            selected_season_key = Some(season_key.clone());
                        }
                        
                        if !season_info.notes.is_empty() {
                            ui.label(format!("| {}", season_info.notes));
                        }
                    });
                }
            });
        });
        
        if back_clicked {
            self.state = AppState::MainMenu;
        }
        
        if let Some(season_key) = selected_season_key {
            self.selected_season = Some(season_key.clone());
            self.start_download(&season_key, false);
        }
    }

    fn show_test_servers(&mut self, ui: &mut egui::Ui) {
        let mut back_clicked = false;
        let mut selected_ts_key: Option<String> = None;
        
        ui.vertical(|ui| {
            ui.horizontal(|ui| {
                if ui.button("← Back to Main Menu").clicked() {
                    back_clicked = true;
                }
                ui.separator();
                ui.heading("Test Server Downloader");
            });
            
            ui.add_space(10.0);
            
            ui.horizontal(|ui| {
                ui.label("Steam Username:");
                let response = ui.text_edit_singleline(&mut self.username);
                if response.changed() {
                    self.username_error.clear();
                }
            });
            
            if !self.username_error.is_empty() {
                ui.colored_label(egui::Color32::RED, &self.username_error);
            }
            
            ui.horizontal(|ui| {
                ui.label("Steam Password:");
                if self.show_password {
                    ui.text_edit_singleline(&mut self.password);
                } else {
                    ui.add(egui::TextEdit::singleline(&mut self.password).password(true));
                }
                ui.checkbox(&mut self.show_password, "Show");
            });
            
            ui.add_space(10.0);
            ui.separator();
            ui.add_space(10.0);
            
            ui.label("Select a Test Server version to download:");
            
            for (ts_key, ts_info) in &self.test_servers {
                ui.horizontal(|ui| {
                    let button_text = format!("{} | {} | {}", ts_info.name, ts_info.year, ts_info.size);
                    if ui.button(button_text).clicked() {
                        selected_ts_key = Some(ts_key.clone());
                    }
                });
            }
        });
        
        if back_clicked {
            self.state = AppState::MainMenu;
        }
        
        if let Some(ts_key) = selected_ts_key {
            self.selected_season = Some(ts_key.clone());
            self.start_download(&ts_key, true);
        }
    }

    fn show_4k_textures(&mut self, ui: &mut egui::Ui) {
        let mut back_clicked = false;
        let mut selected_4k_key: Option<String> = None;
        
        ui.vertical(|ui| {
            ui.horizontal(|ui| {
                if ui.button("← Back to Main Menu").clicked() {
                    back_clicked = true;
                }
                ui.separator();
                ui.heading("4K Textures Download");
            });
            
            ui.add_space(10.0);
            
            ui.horizontal(|ui| {
                ui.label("Steam Username:");
                let response = ui.text_edit_singleline(&mut self.username);
                if response.changed() {
                    self.username_error.clear();
                }
            });
            
            if !self.username_error.is_empty() {
                ui.colored_label(egui::Color32::RED, &self.username_error);
            }
            
            ui.horizontal(|ui| {
                ui.label("Steam Password:");
                if self.show_password {
                    ui.text_edit_singleline(&mut self.password);
                } else {
                    ui.add(egui::TextEdit::singleline(&mut self.password).password(true));
                }
                ui.checkbox(&mut self.show_password, "Show");
            });
            
            ui.add_space(10.0);
            ui.separator();
            ui.add_space(10.0);
            
            ui.label("Select a season to download 4K textures for:");
            
            egui::ScrollArea::vertical().show(ui, |ui| {
                let mut textures: Vec<_> = self.four_k_textures.iter().collect();
                textures.sort_by(|a, b| b.1.0.cmp(&a.1.0)); 
                
                for (name, (year, _manifest)) in textures {
                    ui.horizontal(|ui| {
                        let button_text = format!("{} | {}", name, year);
                        if ui.button(button_text).clicked() {
                            selected_4k_key = Some(name.clone());
                        }
                    });
                }
            });
        });
        
        if back_clicked {
            self.state = AppState::MainMenu;
        }
        
        if let Some(texture_key) = selected_4k_key {
            self.selected_season = Some(format!("{} 4K", texture_key));
            self.start_4k_download(&texture_key);
        }
    }

    fn show_extra_tools(&mut self, ui: &mut egui::Ui) {
        let mut back_clicked = false;
        let mut download_liberator = false;
        let mut download_hm_old = false;
        let mut download_hm_latest = false;
        let mut download_dxvk = false;
        
        ui.vertical(|ui| {
            ui.horizontal(|ui| {
                if ui.button("← Back to Main Menu").clicked() {
                    back_clicked = true;
                }
                ui.separator();
                ui.heading("Extra Tools");
            });
            // Needs error handling and download outputs
            ui.add_space(10.0);
            ui.label("All tools will be downloaded to the Resources/Tools folder.");
            ui.add_space(10.0);
            
            if ui.button("Download Liberator (Y1S0 - Y4S4)").clicked() {
                download_liberator = true;
            }
            ui.add_space(5.0);
            
            if ui.button("Download Heated Metal 0.2.3 (Y5S3 ONLY)").clicked() {
                download_hm_old = true;
            }
            ui.add_space(5.0);
            
            if ui.button("Download Heated Metal Latest (Y5S4 ONLY)").clicked() {
                download_hm_latest = true;
            }
            ui.add_space(5.0);
            
            if ui.button("Download DXVK (Vulkan Renderer)").clicked() {
                download_dxvk = true;
            }
        });
        
        if back_clicked {
            self.state = AppState::MainMenu;
        }
        
        if download_liberator {
            self.download_tool("https://github.com/SlejmUr/Manifest_Tool_TB/raw/main/R6_Liberator_0.0.0.22.exe", "R6_Liberator_0.0.0.22.exe");
        }
        
        if download_hm_old {
            self.download_tool("https://github.com/DataCluster0/HeatedMetal/releases/download/0.2.3/HeatedMetal.7z", "HeatedMetal.7z");
        }
        
        if download_hm_latest {
            if let Err(e) = webbrowser::open("https://github.com/DataCluster0/HeatedMetal/releases/latest") {
                eprintln!("Failed to open browser: {}", e);
            }
        }
        
        if download_dxvk {
            self.download_tool("https://github.com/Vergepoland/r6-downloader/raw/refs/heads/main/Siege-DXVK.zip", "Siege-DXVK.zip");
        }
    }

    fn show_settings(&mut self, ui: &mut egui::Ui) {
        let mut back_clicked = false;
        let mut reset_clicked = false;
        
        ui.vertical(|ui| {
            ui.horizontal(|ui| {
                if ui.button("← Back to Main Menu").clicked() {
                    back_clicked = true;
                }
                ui.separator();
                ui.heading("Settings");
            });
            
            ui.add_space(20.0);
            
            ui.horizontal(|ui| {
                ui.label("Max Download Connections:");
                ui.add(egui::Slider::new(&mut self.max_downloads, 1..=50).text("connections"));
            });
            ui.label("Higher values = faster downloads but more bandwidth usage");
            
            ui.add_space(20.0);
            
            ui.horizontal(|ui| {
                ui.label("Downloads Folder:");
                let mut folder_str = self.downloads_folder.to_string_lossy().to_string();
                if ui.text_edit_singleline(&mut folder_str).changed() {
                    self.downloads_folder = PathBuf::from(folder_str);
                }
                if ui.button("Browse").clicked() {
                    if let Some(path) = rfd::FileDialog::new().pick_folder() {
                        self.downloads_folder = path;
                    }
                }
            });
            
            ui.add_space(20.0);
            
            if ui.button("Reset to Defaults").clicked() {
                reset_clicked = true;
            }
        });
        
        if back_clicked {
            self.state = AppState::MainMenu;
        }
        
        if reset_clicked {
            self.max_downloads = 25;
            self.downloads_folder = PathBuf::from("Downloads");
        }
    }

    fn show_guide(&mut self, ui: &mut egui::Ui) {
        let mut back_clicked = false;
        let mut open_guide = false;
        
        ui.vertical(|ui| {
            ui.horizontal(|ui| {
                if ui.button("← Back to Main Menu").clicked() {
                    back_clicked = true;
                }
                ui.separator();
                ui.heading("Installation Guide and FAQ");
            });
            
            ui.add_space(10.0);
            
            if ui.button("Open Throwback Guide & FAQ (Updated)").clicked() {
                open_guide = true;
            }
            
            ui.add_space(20.0);
            ui.separator();
            ui.add_space(10.0);
            
            ui.heading("Frequently Asked Questions");
            
            egui::ScrollArea::vertical().show(ui, |ui| {
                ui.collapsing("Is it safe to enter my password?", |ui| {
                    ui.label("Yes it is safe. This application uses DepotDownloader, an open-source tool by SteamRE.");
                    ui.label("You can view the source code here: https://github.com/SteamRE/DepotDownloader/");
                });
                
                ui.collapsing("Why do I get 'Invalid Password'?", |ui| {
                    ui.label("You need to enter your LEGACY Steam username, not your profile name.");
                    ui.label("This is the username you use to login to Steam, not your display name.");
                });
                
                ui.collapsing("Where can I change my in-game name?", |ui| {
                    ui.label("In the cplay.ini file located in your downloaded game folder.");
                });
                
                ui.collapsing("Why do I have no RainbowSix.exe file?", |ui| {
                    ui.label("Run the downloader again, selecting the same season to verify files.");
                    ui.label("Also ensure you have enough storage space available.");
                });
                
                ui.collapsing("Why am I getting 'Missing xxxxxxxx.dll' errors?", |ui| {
                    ui.label("Ensure you have an antivirus exclusion set for the downloader folder.");
                    ui.label("Simply turning OFF your antivirus won't work - you MUST set up an exclusion.");
                });
                
                ui.collapsing("How to play with other people?", |ui| {
                    ui.label("1. Download Radmin VPN: https://radmin-vpn.com/");
                    ui.label("2. Create or join a private network");
                    ui.label("3. Create or join a local custom game");
                    ui.label("4. Allow Siege through the firewall in Radmin VPN (System → Firewall)");
                });
                
                ui.collapsing("How to launch the game?", |ui| {
                    ui.label("1. Navigate to your Downloads folder where the game was downloaded");
                    ui.label("2. Double-click RainbowSix.bat (preferred) or RainbowSix.exe");
                    ui.label("3. For some older versions, use RainbowSixGame.exe");
                });
            });
        });
        
        if back_clicked {
            self.state = AppState::MainMenu;
        }
        
        if open_guide {
            if let Err(e) = webbrowser::open("https://puppetino.github.io/Throwback-FAQ") {
                eprintln!("Failed to open browser: {}", e);
            }
        }
    }

    fn show_downloading(&mut self, ui: &mut egui::Ui) {
        ui.vertical(|ui| {
            ui.horizontal(|ui| {
                ui.heading("Download Progress");
                ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                    if ui.button("Cancel Download").clicked() {
                        self.cancel_download();
                    }
                });
            });
            
            ui.add_space(10.0);
            
            if let Some(season_name) = &self.selected_season {
                ui.label(format!("Downloading: {}", season_name));
            }
            
            ui.add_space(10.0);
            
            match &self.download_status {
                DownloadStatus::InProgress => {
                    ui.label("Status: Download in progress...");
                }
                DownloadStatus::Completed => {
                    ui.label("Status: Download completed successfully!");
                    ui.add_space(10.0);
                    if ui.button("Return to Main Menu").clicked() {
                        self.state = AppState::MainMenu;
                        self.download_status = DownloadStatus::NotStarted;
                    }
                }
                DownloadStatus::Failed(error) => {
                    ui.colored_label(egui::Color32::RED, format!("Status: Download failed - {}", error));
                    ui.add_space(10.0);
                    if ui.button("Return to Main Menu").clicked() {
                        self.state = AppState::MainMenu;
                        self.download_status = DownloadStatus::NotStarted;
                    }
                }
                _ => {}
            }
            
            ui.add_space(20.0);
            ui.separator();
            ui.add_space(10.0);
            
            ui.label("Download Output:");
            
            egui::ScrollArea::vertical()
                .stick_to_bottom(true)
                .max_height(400.0)
                .show(ui, |ui| {
                    let output = self.download_output.lock().unwrap();
                    for line in output.iter() {
                        ui.label(line);
                    }
                });
        });
    }
}

fn copy_dir_all(src: &std::path::Path, dst: &std::path::Path) -> std::io::Result<()> {
    std::fs::create_dir_all(dst)?;
    for entry in std::fs::read_dir(src)? {
        let entry = entry?;
        let ty = entry.file_type()?;
        if ty.is_dir() {
            copy_dir_all(&entry.path(), &dst.join(entry.file_name()))?;
        } else {
            std::fs::copy(&entry.path(), &dst.join(entry.file_name()))?;
        }
    }
    Ok(())
}

fn main() -> Result<(), eframe::Error> {
    env_logger::init();
    
    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default()
            .with_inner_size([1000.0, 700.0])
            .with_min_inner_size([800.0, 600.0]),
        ..Default::default()
    };
    
    eframe::run_native(
        "REALM Downloader",
        options,
        Box::new(|_cc| Ok(Box::new(RealmDownloaderApp::default()))),
    )
}

