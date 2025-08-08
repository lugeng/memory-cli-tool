// use std::path::PathBuf;
// use cc;

// fn main() {
//     // let dir: PathBuf = ["C:/Program Files (x86)/RtMidi/include"].iter().collect();
//     let dir: PathBuf = ["rtmidi-6.0.0"].iter().collect();

//     cc::Build::new()
//         .include(&dir);
//         // .file(dir.join("rtmidi_c.cpp"))
//         // .compile("rtmidi.lib");
// }

// extern crate bindgen;

// use std::env;
// use std::path::PathBuf;

// fn main() {
//     let bindings = bindgen::Builder::default()
//         .header("wrapper.h")  // 你的 C 头文件
//         .generate()
//         .expect("Unable to generate bindings");

//     let out_path = PathBuf::from(env::var("OUT_DIR").unwrap());
//     bindings
//         .write_to_file(out_path.join("bindings.rs"))
//         .expect("Couldn't write bindings!");
// }

// fn main() {
//     println!("cargo:rustc-link-search=native=C:/Program Files (x86)/RtMidi/lib");
//     println!("cargo:rustc-link-lib=static=rtmidi");
// }

extern crate cc;
// set PKG_CONFIG_PATH=C:/Program Files (x86)/RtMidi/lib/pkgconfig/rtmidi.pc;%PKG_CONFIG_PATH%
fn main() {
    // println!("cargo:rustc-link-search=native={}", "C:/Program Files (x86)/RtMidi/lib");
    // println!("cargo:rustc-link-lib=static={}", "rtmidi");
}
