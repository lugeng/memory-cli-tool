
use std::cell::RefCell;
use std::error::Error;
use std::{fs, thread};
use std::io::{stdin, stdout, Write};
use std::rc::Rc;
use std::sync::{Arc, Mutex};

use midir::{Ignore, MidiInput};
use midly::{MidiMessage, Smf, Header, parse};
use midly::live::LiveEvent;
use midly::num::{u15, u28, u7, u4, u24};

fn main() {
    match run() {
        Ok(_) => (),
        Err(err) => println!("Error: {}", err),
    }
}

fn format_message(bytes: &[u8]) -> String {
    let mut s = String::new();
    if bytes.len() > 1 {
        s.push_str(&format!("{:04b} {:04b} ", bytes[0]>>4, bytes[0]&0x0f));
    }
    for &byte in bytes[1..].iter() {
        s.push_str(&format!("{} ", byte));
    }
    s
}

fn bpm_to_microseconds_per_beat(bpm: f32) -> u24 {
    u24::from((60_000_000.0 / bpm) as u32)
}

fn save_midi_test(events: Vec<(u64, Vec<u8>)>) {
    println!("got {} events", events.len());
    let mut my = Smf::new(Header {
        format: midly::Format::Parallel,
        timing: midly::Timing::Metrical(u15::from(480)),
    });
    // 元信息轨道
    let mut meta_track = midly::Track::new();
    // 3/4 拍，每拍 24 个 tick，每个四分音符 = 8 个 32 分音符
    meta_track.push(midly::TrackEvent {
        delta: u28::from(0),
        kind: midly::TrackEventKind::Meta(midly::MetaMessage::TimeSignature(3, 4, 24, 8)),
    });
    // 调号，0 个升号（正数为升，负数为降），C 大调，false/true 代表大调还是小调
    meta_track.push(midly::TrackEvent { 
        delta: u28::from(0), 
        kind: midly::TrackEventKind::Meta(midly::MetaMessage::KeySignature(0, false)),
    });
    // 一拍的微秒数量，这里是 80bpm
    meta_track.push(midly::TrackEvent {
        delta: u28::from(0),
        kind: midly::TrackEventKind::Meta(midly::MetaMessage::Tempo(bpm_to_microseconds_per_beat(80.0))),
    });
    // 结束
    meta_track.push(midly::TrackEvent {
        delta: u28::from(0),
        kind: midly::TrackEventKind::Meta(midly::MetaMessage::EndOfTrack),
    });
    my.tracks.push(meta_track);
    // 乐符轨道
    let mut track = midly::Track::new();
    track.push(midly::TrackEvent {
        delta: u28::from(0),
        kind: midly::TrackEventKind::Midi { 
            channel: u4::from(0),
            message: midly::MidiMessage::Controller { controller: u7::from(0), value: u7::from(0) } 
        },
    });
    track.push(midly::TrackEvent {
        delta: u28::from(0),
        kind: midly::TrackEventKind::Midi { 
            channel: u4::from(0),
            message: midly::MidiMessage::Controller { controller: u7::from(37), value: u7::from(0) } 
        },
    });
    track.push(midly::TrackEvent {
        delta: u28::from(0),
        kind: midly::TrackEventKind::Midi { 
            channel: u4::from(0),
            message: midly::MidiMessage::ProgramChange { program: u7::from(0) },
        },
    });
    track.push(midly::TrackEvent {
        delta: u28::from(0),
        kind: midly::TrackEventKind::Meta(midly::MetaMessage::TrackName("My Test".as_bytes())),
    });
    let mut last_ts = 0;
    for event in events {
        let (ts, message) = event;
        let delta = 32 * (ts - last_ts) / 1000;
        last_ts = ts;
        let event = LiveEvent::parse(message.as_slice()).unwrap();
        match event {
            LiveEvent::Midi { channel, message } => match message {
                MidiMessage::NoteOn { key, vel } => {
                    println!("{}: NoteOn {} vel {}", ts, key, vel);
                    track.push(midly::TrackEvent {
                        delta: u28::from(delta as u32),
                        kind: midly::TrackEventKind::Midi { 
                            channel: u4::from(channel), 
                            message: midly::MidiMessage::NoteOn { key: u7::from(key), vel: u7::from(vel) } 
                        },
                    });
                }
                _ => {}
            },
            _ => {}
        }
    }
    track.push(midly::TrackEvent {
        delta: u28::from(1),
        kind: midly::TrackEventKind::Meta(midly::MetaMessage::EndOfTrack),
    });
    my.tracks.push(track);

    my.save("test-asset/RiversFlowsInYou_new.mid").unwrap();
}

fn run() -> Result<(), Box<dyn Error>> {
    // read_midi_test();
    // Ok(())

    let mut input = String::new();

    let mut midi_in = MidiInput::new("midir reading input")?;
    midi_in.ignore(Ignore::None);

    // Get an input port (read from console if multiple are available)
    let in_ports = midi_in.ports();
    let in_port = match in_ports.len() {
        0 => return Err("no input port found".into()),
        1 => {
            println!(
                "Choosing the only available input port: {}",
                midi_in.port_name(&in_ports[0]).unwrap()
            );
            &in_ports[0]
        }
        _ => {
            println!("\nAvailable input ports:");
            for (i, p) in in_ports.iter().enumerate() {
                println!("{}: {}", i, midi_in.port_name(p).unwrap());
            }
            print!("Please select input port: ");
            stdout().flush()?;
            let mut input = String::new();
            stdin().read_line(&mut input)?;
            in_ports
                .get(input.trim().parse::<usize>()?)
                .ok_or("invalid input port selected")?
        }
    };

    println!("\nOpening connection");
    let in_port_name = midi_in.port_name(in_port)?;

    let mut events:Vec<(u64, Vec<u8>)> = Vec::new();
    // _conn_in needs to be a named parameter, because it needs to be kept alive until the end of the scope
    let _conn_in = midi_in.connect(
        in_port,
        "midir-read-input",
        move |stamp, message, events| {
            println!("{}: {}", stamp, format_message(message));
            let msg = message.to_vec();
            events.push((stamp, msg));
        },
        events,
    )?;

    println!(
        "Connection open, reading input from '{}' (press enter to exit) ...",
        in_port_name
    );

    input.clear();
    stdin().read_line(&mut input)?; // wait for next enter key press

    println!("Closing connection");
    let (_, events) = _conn_in.close();

    save_midi_test(events);

    Ok(())
}