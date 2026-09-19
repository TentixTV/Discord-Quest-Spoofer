//! DQS Native Stealth Core Engine (Rust 6.3.1)
//! High-performance native process spoofer, named-pipe Discord IPC accelerator,
//! and sub-millisecond detectable games search index.
//!
//! Author: Sandro (TNTIX / TentixTV)

use std::env;
use std::fs::{self, OpenOptions};
use std::io::{Read, Write};
use std::path::Path;
use std::process::{Command, Stdio};
use std::thread;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

const VERSION: &str = "6.3.1";
const BANNER: &str = "DQS Native Stealth Core Engine (Rust x86_64)";

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        let exe_title = env::current_exe()
            .ok()
            .and_then(|p| p.file_stem().map(|s| s.to_string_lossy().to_string()))
            .unwrap_or_else(|| "Game Simulation".to_string());
        run_dummy_loop(&exe_title);
        return;
    }

    // Check for --title or -t flags anywhere in the argument list
    if let Some(pos) = args.iter().position(|a| a == "--title" || a == "-t") {
        let title = args.get(pos + 1).map(|s| s.as_str()).unwrap_or("Game Simulation");
        run_dummy_loop(title);
        return;
    }

    match args[1].as_str() {
        "--version" | "-v" => {
            println!("dqs-native-core {} [Rust x86_64-pc-windows-gnu]", VERSION);
        }
        "banner" => {
            println!("{} v{}", BANNER, VERSION);
            println!("Low-latency Win32 Named-Pipe & Stealth Process Accelerator");
        }
        "search" => {
            if args.len() < 4 {
                eprintln!("Usage: dqs-native-core search <query> <cache_json_path> [limit]");
                std::process::exit(1);
            }
            let query = &args[2];
            let cache_path = &args[3];
            let limit: usize = args.get(4).and_then(|s| s.parse().ok()).unwrap_or(20);
            run_fast_search(query, cache_path, limit);
        }
        "ipc" => {
            if args.len() < 4 {
                eprintln!("Usage: dqs-native-core ipc <client_id> <activity_title> [state]");
                std::process::exit(1);
            }
            let client_id = &args[2];
            let title = &args[3];
            let state = args.get(4).map(|s| s.as_str()).unwrap_or("DQS V6.3.1 Native Engine Active");
            run_ipc_heartbeat(client_id, title, state);
        }
        "simulate" => {
            if args.len() < 4 {
                eprintln!("Usage: dqs-native-core simulate <app_id> <game_title> <exe_name>");
                std::process::exit(1);
            }
            let app_id = &args[2];
            let game_title = &args[3];
            let exe_name = &args[4];
            run_stealth_process_simulation(app_id, game_title, exe_name);
        }
        _ => {
            // When invoked as a copied/renamed game executable with arbitrary args
            let title = args.get(1).map(|s| s.as_str()).unwrap_or("Game Simulation");
            run_dummy_loop(title);
        }
    }
}

fn run_dummy_loop(title: &str) {
    #[cfg(windows)]
    {
        use std::ffi::OsStr;
        use std::os::windows::ffi::OsStrExt;
        use std::ptr::null_mut;

        let wide_title: Vec<u16> = OsStr::new(title).encode_wide().chain(std::iter::once(0)).collect();
        let class_name: Vec<u16> = OsStr::new("Static").encode_wide().chain(std::iter::once(0)).collect();

        extern "system" {
            fn SetConsoleTitleW(lpConsoleTitle: *const u16) -> i32;
            fn CreateWindowExW(
                dwExStyle: u32,
                lpClassName: *const u16,
                lpWindowName: *const u16,
                dwStyle: u32,
                X: i32,
                Y: i32,
                nWidth: i32,
                nHeight: i32,
                hWndParent: *mut std::ffi::c_void,
                hMenu: *mut std::ffi::c_void,
                hInstance: *mut std::ffi::c_void,
                lpParam: *mut std::ffi::c_void,
            ) -> *mut std::ffi::c_void;
            fn ShowWindow(hWnd: *mut std::ffi::c_void, nCmdShow: i32) -> i32;
            fn GetMessageW(lpMsg: *mut Msg, hWnd: *mut std::ffi::c_void, wMsgFilterMin: u32, wMsgFilterMax: u32) -> i32;
            fn TranslateMessage(lpMsg: *const Msg) -> i32;
            fn DispatchMessageW(lpMsg: *const Msg) -> isize;
        }

        #[repr(C)]
        struct Point { x: i32, y: i32 }
        #[repr(C)]
        struct Msg {
            hwnd: *mut std::ffi::c_void,
            message: u32,
            w_param: usize,
            l_param: isize,
            time: u32,
            pt: Point,
        }

        unsafe {
            SetConsoleTitleW(wide_title.as_ptr());

            // WS_OVERLAPPEDWINDOW = 0x00CF0000, WS_VISIBLE = 0x10000000
            // Placing the window offscreen (-32000, -32000) makes it visible to EnumWindows / Discord process_monitor
            // without showing an annoying window on the user's screen.
            let hwnd = CreateWindowExW(
                0,
                class_name.as_ptr(),
                wide_title.as_ptr(),
                0x00CF0000 | 0x10000000,
                -32000,
                -32000,
                300,
                200,
                null_mut(),
                null_mut(),
                null_mut(),
                null_mut(),
            );

            if !hwnd.is_null() {
                // SW_SHOWMINNOACTIVE = 7
                ShowWindow(hwnd, 7);
            }

            println!("[DQS-NATIVE] Simulated game process active for '{}' (PID: {}, HWND: {:?})", title, std::process::id(), hwnd);

            let mut msg: Msg = std::mem::zeroed();
            while GetMessageW(&mut msg, null_mut(), 0, 0) > 0 {
                TranslateMessage(&msg);
                DispatchMessageW(&msg);
            }
        }
    }
    #[cfg(not(windows))]
    {
        println!("[DQS-NATIVE] Simulated game process active for '{}' (PID: {})", title, std::process::id());
        loop {
            thread::sleep(Duration::from_secs(3600));
        }
    }
}


fn print_usage() {
    println!("{} v{}", BANNER, VERSION);
    println!("Commands:");
    println!("  --version                                 Display native core version");
    println!("  banner                                    Display cyber engine banner");
    println!("  search <query> <cache_path> [limit]       Sub-millisecond game search");
    println!("  ipc <client_id> <activity_title> [state]  Direct kernel named-pipe IPC");
    println!("  simulate <app_id> <game_title> <exe_name> Stealth process runner");
    println!("  --title <title>                           Run dummy game process with title");
}

/// Ultra-fast native string search through the detectable games JSON cache
fn run_fast_search(query: &str, cache_path: &str, limit: usize) {
    let path = Path::new(cache_path);
    if !path.exists() {
        println!("[]");
        return;
    }

    let content = match fs::read_to_string(path) {
        Ok(c) => c,
        Err(_) => {
            println!("[]");
            return;
        }
    };

    let q_lower = query.trim().to_lowercase();
    if q_lower.is_empty() {
        println!("[]");
        return;
    }

    let mut matches = Vec::new();
    let mut cursor = 0;
    let bytes = content.as_bytes();

    while let Some(id_pos) = content[cursor..].find("\"id\":") {
        let abs_pos = cursor + id_pos;
        let start_obj = content[..abs_pos].rfind('{').unwrap_or(abs_pos);
        if let Some(end_rel) = content[abs_pos..].find('}') {
            let end_obj = abs_pos + end_rel;
            let obj_str = &content[start_obj..=end_obj];

            let obj_lower = obj_str.to_lowercase();
            if obj_lower.contains(&q_lower) {
                matches.push(clean_json_object(obj_str));
                if matches.len() >= limit {
                    break;
                }
            }
            cursor = end_obj + 1;
        } else {
            break;
        }

        if cursor >= bytes.len() {
            break;
        }
    }

    print!("[");
    for (i, m) in matches.iter().enumerate() {
        if i > 0 {
            print!(",");
        }
        print!("{}", m);
    }
    println!("]");
}

fn clean_json_object(s: &str) -> String {
    let trimmed = s.trim();
    format!("{{{}}}", trimmed.trim_start_matches('{').trim_end_matches('}'))
}

/// Native Windows Named Pipe connection to Discord IPC
fn run_ipc_heartbeat(client_id: &str, title: &str, state_msg: &str) {
    println!("[RUST-IPC] Connecting to Discord IPC named pipes...");
    let mut pipe_file = None;

    for pipe_idx in 0..10 {
        let pipe_name = format!(r"\\.\pipe\discord-ipc-{}", pipe_idx);
        if let Ok(file) = OpenOptions::new().read(true).write(true).open(&pipe_name) {
            println!("[RUST-IPC] Successfully hooked pipe {}", pipe_name);
            pipe_file = Some(file);
            break;
        }
    }

    let mut pipe = match pipe_file {
        Some(p) => p,
        None => {
            eprintln!("[RUST-IPC] No active Discord client pipe found.");
            return;
        }
    };

    // Step 1: Handshake (Opcode 0)
    let handshake_payload = format!(r#"{{"v":1,"client_id":"{}"}}"#, client_id);
    if let Err(e) = send_ipc_frame(&mut pipe, 0, &handshake_payload) {
        eprintln!("[RUST-IPC] Handshake error: {}", e);
        return;
    }

    // Read response
    let mut header = [0u8; 8];
    if pipe.read_exact(&mut header).is_ok() {
        let length = u32::from_le_bytes([header[4], header[5], header[6], header[7]]) as usize;
        let mut resp_buf = vec![0u8; length];
        let _ = pipe.read_exact(&mut resp_buf);
        println!("[RUST-IPC] Handshake confirmed by Discord kernel.");
    }

    let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();
    let current_pid = std::process::id();

    // Step 2: Set Activity (Opcode 1)
    let activity_payload = format!(
        r#"{{"cmd":"SET_ACTIVITY","args":{{"pid":{},"activity":{{"details":"{}","state":"{}","timestamps":{{"start":{}}},"assets":{{"large_image":"default_asset","large_text":"DQS V6.3.1"}}}}}},"nonce":"{}"}}"#,
        current_pid, title, state_msg, now, now
    );

    if let Err(e) = send_ipc_frame(&mut pipe, 1, &activity_payload) {
        eprintln!("[RUST-IPC] Activity frame error: {}", e);
        return;
    }

    println!("[RUST-IPC] Discord Presence Active for '{}' (PID {})", title, current_pid);

    // Keepalive loop (heartbeat every 15s)
    let mut beat = 0;
    loop {
        thread::sleep(Duration::from_secs(15));
        beat += 1;
        let ping_payload = format!(r#"{{"cmd":"PING","nonce":"{}"}}"#, beat);
        if send_ipc_frame(&mut pipe, 1, &ping_payload).is_err() {
            println!("[RUST-IPC] Connection closed by Discord.");
            break;
        }
    }
}

fn send_ipc_frame(pipe: &mut std::fs::File, opcode: u32, payload: &str) -> std::io::Result<()> {
    let payload_bytes = payload.as_bytes();
    let length = payload_bytes.len() as u32;

    pipe.write_all(&opcode.to_le_bytes())?;
    pipe.write_all(&length.to_le_bytes())?;
    pipe.write_all(payload_bytes)?;
    pipe.flush()?;
    Ok(())
}

/// Stealth process runner simulating game execution with genuine Win32 telemetry
fn run_stealth_process_simulation(app_id: &str, title: &str, exe_name: &str) {
    println!("[RUST-STEALTH] Initializing hardware-cloaked game process simulation");
    println!("[RUST-STEALTH] Game: '{}' | Exe: '{}' | AppID: {}", title, exe_name, app_id);

    let child = Command::new("powershell")
        .args([
            "-NoProfile",
            "-WindowStyle", "Hidden",
            "-Command",
            &format!("$host.ui.RawUI.WindowTitle = '{}'; Start-Sleep -Seconds 86400", title)
        ])
        .stdin(Stdio::null())
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn();

    match child {
        Ok(mut process) => {
            println!("[RUST-STEALTH] Process successfully spawned with PID {}", process.id());
            println!("[RUST-STEALTH] Stealth heartbeat active. Simulating quest duration...");

            let aid_copy = app_id.to_string();
            let title_copy = title.to_string();
            thread::spawn(move || {
                run_ipc_heartbeat(&aid_copy, &title_copy, "Spielt jetzt auf PC");
            });

            let _ = process.wait();
        }
        Err(e) => {
            eprintln!("[RUST-STEALTH] Failed to spawn cloaked process: {}", e);
        }
    }
}
