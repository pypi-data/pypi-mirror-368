use crate::endpoints::worker_group_endpoint::WorkerGroupEndpoint;

use thava_types::{
    worker_admin::WorkerAdminId,
    worker_group::{WorkerGroup, WorkerGroupId, WorkerGroupName},
    worker_machine::{DeviceStatuses, Gpus, WorkerMachine, WorkerMachineId, WorkerMachineStatus},
};

use anyhow::Result;
use std::{collections::HashMap, io};
use tokio::sync::mpsc;
use tracing::info;

use crossterm::event::{self, Event, KeyCode, KeyEvent, KeyEventKind};
use ratatui::{
    buffer::Buffer,
    layout::Rect,
    style::Stylize,
    symbols::border,
    text::{Line, Text},
    widgets::{Block, Paragraph, Widget},
    DefaultTerminal, Frame,
};

#[derive(Debug)]
struct GroupApp {
    groups: Vec<WorkerGroup>,
    groups_receiver: mpsc::Receiver<Vec<WorkerGroup>>,
    exit: bool,
}

impl GroupApp {
    /// runs the application's main loop until the user quits
    pub fn run(&mut self, terminal: &mut DefaultTerminal) -> io::Result<()> {
        while !self.exit {
            info!("Drawing terminal");
            terminal.draw(|frame| self.draw(frame))?;
            info!("Handling events");
            self.handle_events()?;
            info!("Clearing terminal");
        }
        Ok(())
    }

    fn draw(&mut self, frame: &mut Frame) {
        frame.render_widget(self, frame.area());
    }

    fn handle_events(&mut self) -> io::Result<()> {
        match event::poll(std::time::Duration::from_millis(100)) {
            Ok(true) => {
                match event::read()? {
                    // it's important to check that the event is a key press event as
                    // crossterm also emits key release and repeat events on Windows.
                    Event::Key(key_event) if key_event.kind == KeyEventKind::Press => {
                        self.handle_key_event(key_event)
                    }
                    _ => {}
                };
            }
            Ok(false) => return Ok(()),
            Err(e) => return Err(e),
        }

        Ok(())
    }

    fn handle_key_event(&mut self, key_event: KeyEvent) {
        if let KeyCode::Char('q') = key_event.code {
            self.exit()
        }
    }

    fn exit(&mut self) {
        self.exit = true;
    }

    fn render_group(
        &self,
        i: usize,
        group: &WorkerGroup,
        num_groups: usize,
        inner_area: Rect,
        buf: &mut Buffer,
    ) {
        let group_name = Line::from(format!(" {} ", group.name));
        let group_block = Block::bordered()
            .title(group_name.centered())
            .border_set(border::PLAIN);

        let mut group_area = inner_area;
        group_area.height = inner_area.height / num_groups as u16;
        group_area.y += i as u16 * group_area.height;

        let machines_area = group_block.inner(group_area);

        group.machines.iter().enumerate().for_each(|(i, machine)| {
            self.render_machine(i, group, machine, machines_area, buf);
        });

        group_block.render(group_area, buf);
    }

    fn render_machine(
        &self,
        i: usize,
        group: &WorkerGroup,
        machine: &WorkerMachine,
        machines_area: Rect,
        buf: &mut Buffer,
    ) {
        let machine1 = Line::from(format!(" {} ", machine.id));
        let machine_block = Block::bordered()
            .title(machine1.centered())
            .border_set(border::PLAIN);

        let mut machine1_area = machines_area;
        machine1_area.width = machines_area.width / group.machines.len() as u16;
        machine1_area.x += i as u16 * machine1_area.width;

        let mut gpu_lines = Vec::new();
        machine.gpus.iter().for_each(|(gpu_id, gpu_name)| {
            gpu_lines.push(Line::from(format!(" {gpu_id}: {gpu_name} ")));
        });

        let gpus = Paragraph::new(Text::from(gpu_lines));

        gpus.block(machine_block).render(machine1_area, buf);
    }
}

impl Widget for &mut GroupApp {
    fn render(self, area: Rect, buf: &mut Buffer) {
        info!("Rendering groups");
        let title = Line::from(" Caravan Worker Groups ".bold());
        let instructions = Line::from(vec![" Quit ".into(), "<Q> ".blue().bold()]);
        let block = Block::bordered()
            .title(title.centered())
            .title_bottom(instructions.centered())
            .border_set(border::THICK);
        let inner_area = block.inner(area);

        match self.groups_receiver.try_recv() {
            Ok(groups) => {
                info!("Received groups: {:?}", groups);
                self.groups = groups;
            }
            Err(e) => {
                info!("Error receiving groups: {:?}", e);
            }
        }

        self.groups.iter().enumerate().for_each(|(i, group)| {
            self.render_group(i, group, self.groups.len(), inner_area, buf);
        });

        block.render(area, buf);
    }
}

fn _example_groups() -> Vec<WorkerGroup> {
    let mut gpus = HashMap::new();
    gpus.insert(0, "NVIDIA Tesla V100".to_string());
    gpus.insert(1, "NVIDIA Tesla V100".to_string());

    vec![
        WorkerGroup {
            id: WorkerGroupId::new(),
            name: WorkerGroupName::new("amitgroup"),
            clients: HashMap::new(),
            machines: vec![
                WorkerMachine::new(
                    WorkerMachineId::new(),
                    gpus.into(),
                    WorkerAdminId::new(),
                    WorkerMachineStatus::Available,
                    DeviceStatuses::default(),
                ),
                WorkerMachine::new(
                    WorkerMachineId::new(),
                    Gpus::new(),
                    WorkerAdminId::new(),
                    WorkerMachineStatus::Available,
                    DeviceStatuses::default(),
                ),
            ],
        },
        WorkerGroup {
            id: WorkerGroupId::new(),
            name: WorkerGroupName::new("shravangroup"),
            clients: HashMap::new(),
            machines: vec![],
        },
        WorkerGroup {
            id: WorkerGroupId::new(),
            name: WorkerGroupName::new("khalilgroup"),
            clients: HashMap::new(),
            machines: vec![],
        },
    ]
}

async fn update_groups(groups_sender: mpsc::Sender<Vec<WorkerGroup>>) -> Result<()> {
    tokio::spawn(async move {
        let mut worker_group_endpoint = WorkerGroupEndpoint::new_with_auth().await?;
        let duration = std::time::Duration::from_secs(2);

        loop {
            info!("Updating groups");
            let groups = worker_group_endpoint.list_groups().await?;

            groups_sender.send(groups).await?;

            tokio::time::sleep(duration).await;
        }

        #[allow(unreachable_code)]
        Ok::<(), anyhow::Error>(())
    });

    Ok(())
}

pub async fn list() -> Result<()> {
    let mut terminal = ratatui::init();
    let groups = Vec::new();

    let (groups_sender, groups_receiver) = mpsc::channel(1);

    match update_groups(groups_sender).await {
        Ok(ok) => {
            info!("Updated groups: {:?}", ok);
        }
        Err(e) => {
            info!("Error updating groups: {:?}", e);
        }
    }

    let mut group_app = GroupApp {
        groups,
        groups_receiver,
        exit: false,
    };

    group_app.run(&mut terminal)?;

    ratatui::restore();

    Ok(())
}
