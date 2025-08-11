from textual.app import App, ComposeResult, Screen
from textual.widgets import Static, Input, Label, Button, Link, Header
from textual.containers import Container, Horizontal, VerticalScroll, Vertical
from rich.segment import Segment
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from SOM_TUI.main import main
import requests
from textual.style import Style
from PIL import Image
from io import BytesIO
import subprocess
import mpv
from rich_pixels import Pixels
from rich.console import Console
class Screen1(Screen):
    CSS_PATH = "landing.tcss"
    print("hi")
    def compose(self) -> ComposeResult:
        yield Label("Paste the cookie value of _journey_session from your storage tab in devtools to start voting via the terminal!", classes="welcome-label")
        yield Input(placeholder="Cookies", id="cookie-input")
    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.value:
            with open("som-cookie.txt", "w") as f:
                f.write(event.value)
            self.app.push_screen(Screen2())
class Screen2(Screen):
    CSS_PATH = "layout.tcss"
    def compose(self) -> ComposeResult:
        scraper_stuff = main(driver=self.app.driver)
        self.left_project = scraper_stuff[0]
        self.right_project = scraper_stuff[1]
        self.devlog_1 = scraper_stuff[2]
        self.time_1 = scraper_stuff[3]
        self.devlog_2 = scraper_stuff[4]
        self.time_2 = scraper_stuff[5]
        important_buttons = scraper_stuff[6]
        self.usernames = scraper_stuff[7]
        left_devlogs = scraper_stuff[8]
        left_stuff = scraper_stuff[9]
        right_stuff = scraper_stuff[10]
        right_devlogs = scraper_stuff[11]
        self.left_description = scraper_stuff[12]
        self.right_description = scraper_stuff[13]
        self.driver = scraper_stuff[14]
        self.left_button = scraper_stuff[15]
        self.right_button = scraper_stuff[16]
        self.tie_button = scraper_stuff[17]
        self.feedback_form = scraper_stuff[18]
        self.submit_button = scraper_stuff[19]
        self.ai_tags = scraper_stuff[20]
        self.demo_1 = important_buttons[0].get("href") if len(important_buttons) > 0 else ""
        self.repo_1 = important_buttons[1].get("href") if len(important_buttons) > 1 else ""
        self.demo_2 = important_buttons[2].get("href") if len(important_buttons) > 2 else ""
        self.repo_2 = important_buttons[3].get("href") if len(important_buttons) > 3 else ""
        self.left_images = scraper_stuff[21]
        self.right_images = scraper_stuff[22]
        # Devlog widgets
        self.left_devlog_widgets = []
        for i in range(len(left_devlogs)):
            widgets = []
            widgets.append(
                Static(
                    f"[b]{left_stuff[i]}[/b]\n{left_devlogs[i].text.strip()}",
                    classes="left-quarter-devlogs"
                )
            )
            if i < len(self.left_images) and self.left_images[i][1] == "image":
                image = Image.open(BytesIO(requests.get(self.left_images[i][0]).content))
                image = image.resize((176, 20))
                widgets.append(Static(Pixels.from_image(image)))
            else:
                widgets.append(Link(
                    "Download Link for Devlog Video",
                    classes="left-quarter-demo",
                    url=self.left_images[i][0]
                ))
            self.left_devlog_widgets.extend(widgets)

        self.right_devlog_widgets = []
        for i in range(len(right_devlogs)):
            widgets = []
            widgets.append(
                Static(
                    f"[b]{right_stuff[i].strip()}[/b]\n{right_devlogs[i].text.strip()}".replace("•", ""),
                    classes="right-quarter-devlogs"
                )
            )
            if i < len(self.right_images) and self.right_images[i][1] == "image":
                image = Image.open(BytesIO(requests.get(self.right_images[i][0]).content))
                image = image.resize((176, 20))
                widgets.append(Static(Pixels.from_image(image)))
            else:
                widgets.append(Button(
                    "Download Link for Devlog Video",
                    url=self.right_images[i][0],
                    classes="right-quarter-demo"
                ))
            self.right_devlog_widgets.extend(widgets)
        yield Horizontal(
            VerticalScroll(
                Label(self.left_project, classes="left-quarter"),
                *((Static('Used AI', classes="used-ai-tag"),) if self.ai_tags[0] else ()),
                Label("By:" + self.usernames[0].get("alt"), classes="left-quarter-by"),
                Static(self.devlog_1, classes="left-quarter-devlog-and-time"),
                Static(self.time_1, classes="left-quarter-devlog-and-time"),
                Static(self.left_description, classes="description"),
                Horizontal(
                    Link(
                        "Go to demo",
                        url=self.demo_1,
                        tooltip="Click me",
                        classes="left-quarter-demo"
                    ),
                    Link(
                        "Go to repo",
                        url=self.repo_1,
                        tooltip="Click me",
                        classes="left-quarter-repo"
                    )
                ),
                *self.left_devlog_widgets,
                classes="whole-devlog"
            ),
            VerticalScroll(
                Label(self.right_project, classes="right-quarter"),
                *((Label('Used AI', classes="used-ai-tag"),) if self.ai_tags[1] else ()),
                Label("By:" + self.usernames[1].get("alt"), classes="right-quarter-by"),
                Static(self.devlog_2, classes="right-quarter-devlog-and-time"),
                Static(self.time_2, classes="right-quarter-devlog-and-time"),
                Static(self.right_description, classes="description"),
                Horizontal(
                    Link(
                        "Go to demo",
                        url=self.demo_2,
                        tooltip="Click me",
                        classes="right-quarter-demo"
                    ),
                    Link(
                        "Go to repo",
                        url=self.repo_2,
                        tooltip="Click me",
                        classes="right-quarter-repo"
                    )
                ),
                *self.right_devlog_widgets,
                classes="whole-devlog"
            ),
            classes="screen"
        )
        print(self.left_project, self.right_project, self.left_button, self.right_button, self.tie_button)
        yield Input(placeholder="Type the project you want to vote for here:", id="vote-input")
        yield Static("Write your feedback here:", classes="vote-input")
        yield Input(placeholder="Why did you vote for this project?", id="vote-inputs")
    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "vote-input":
            if event.value.lower() == self.left_project.lower():
                self.driver.execute_script("arguments[0].click();", self.left_button)
            elif event.value.lower() == self.right_project.lower():
                self.driver.execute_script("arguments[0].click();", self.right_button)
            elif event.value.lower() == "tie":
                self.driver.execute_script("arguments[0].click();", self.tie_button)
            else:
                    print("Invalid project name. Please enter either the left or right project name, or 'tie'.")
        elif event.input.id == "vote-inputs":
            self.feedback_form.send_keys(event.value)
            print("Vote submitted successfully!")
            self.driver.execute_script("arguments[0].click();", self.submit_button)
            Static("Vote submitted successfully!", classes="vote-success")
            if self.app:
                self.app.push_screen(Screen2())
            else:
                print("Please enter your feedback before submitting.")
class Voting(App):
    SCREENS = {"screen_one": Screen1, "screen_two": Screen2}

    def on_mount(self) -> None:
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.push_screen(Screen1())
if __name__ == "__main__":
    print("Welcome to the SOM CLI Voting App!")
    app = Voting()
    app.run()