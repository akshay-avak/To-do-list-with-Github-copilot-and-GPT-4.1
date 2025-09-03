from task_storage import TaskStorage
from kivy.uix.spinner import Spinner
import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.widget import Widget

kivy.require('2.0.0')

from datetime import datetime, date


class Task(BoxLayout):
    title = StringProperty("")
    description = StringProperty("")
    due_date = StringProperty("")
    status = StringProperty("Pending")  # 'Pending', 'In-Progress', 'Completed'
    app_ref = ObjectProperty(None)

    def __init__(self, title, description, app_ref, due_date="", status="Pending", **kwargs):
        super().__init__(orientation='vertical', padding=5, spacing=3, **kwargs)
        with self.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            self.bg_color = Color(243/255, 244/255, 246/255, 1)  # Light Gray background for task box
            self.bg_rect = RoundedRectangle(radius=[10], pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        self.title = title
        self.description = description
        self.due_date = due_date
        self.status = status
        self.app_ref = app_ref
        self.build_task()

    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def is_overdue(self):
        if self.status == "Completed":
            return False
        if not self.due_date:
            return False
        try:
            due = datetime.strptime(self.due_date, "%Y-%m-%d").date()
            return due < date.today()
        except Exception:
            return False

    def build_task(self):
        self.clear_widgets()
        self.size_hint_y = None
        min_height = 100
        if self.description:
            min_height += 30
        self.height = min_height

        # Visual indicators for status
        if self.status == "Completed":
            self.bg_color.rgba = [0.8, 1, 0.8, 1]  # Light green for completed
        elif self.status == "In-Progress":
            self.bg_color.rgba = [0.7, 0.85, 1, 1]  # Light blue for in-progress
        elif self.is_overdue():
            self.bg_color.rgba = [1, 0.85, 0.85, 1]  # Light red
        elif self.status == "Pending":
            self.bg_color.rgba = [1, 0.93, 0.7, 1]  # Light orange for pending (urgency)
        else:
            self.bg_color.rgba = [243/255, 244/255, 246/255, 1]

        row = BoxLayout(orientation='horizontal', padding=[0, 5, 0, 5], spacing=10, size_hint_x=1)
        left_col = BoxLayout(orientation='vertical', size_hint_x=1, spacing=2, padding=[10, 10, 10, 10])
        # Title label with strikethrough and checkmark if completed
        title_markup = f'[s]{self.title}[/s]' if self.status == "Completed" else self.title
        title_color = [0.5, 0.5, 0.5, 1] if self.status == "Completed" else ([1, 0, 0, 1] if self.is_overdue() else [31/255, 41/255, 55/255, 1])
        title_icon = "\u2713  " if self.status == "Completed" else ""
        title_label = Label(text=title_icon + title_markup, markup=True, bold=True, color=title_color, halign='left', valign='middle', size_hint_y=None, height=30)
        title_label.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        left_col.add_widget(title_label)
        # Description label
        desc_color = [0.5, 0.5, 0.5, 1] if self.status == "Completed" else [31/255, 41/255, 55/255, 1]
        if self.description:
            desc_label = Label(text=self.description, color=desc_color, halign='left', valign='top', size_hint_y=None, height=30)
            desc_label.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
            left_col.add_widget(desc_label)
        # Due date label
        due_text = f"Due: {self.due_date}" if self.due_date else "No due date"
        due_color = [0.5, 0.5, 0.5, 1] if self.status == "Completed" else ([1, 0, 0, 1] if self.is_overdue() else [31/255, 41/255, 55/255, 1])
        due_label = Label(text=due_text, color=due_color, halign='left', valign='top', size_hint_y=None, height=25, font_size=14)
        due_label.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        left_col.add_widget(due_label)

        right_col = BoxLayout(orientation='vertical', size_hint_x=None, width=270, spacing=10, padding=[0, 10, 0, 10])
        btn_row1 = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=40)
        # Status spinner
        status_spinner = Spinner(
            text=self.status,
            values=["Pending", "In-Progress", "Completed"],
            size_hint_x=None, width=110, height=40, font_size=16
        )
        status_spinner.bind(text=self.on_status_change)
        btn_row1.add_widget(status_spinner)
        # Edit and delete buttons
        edit_btn = Button(text='Edit', size_hint_x=None, width=70, height=40, font_size=16, background_color=[59/255, 130/255, 246/255, 1], color=[1, 1, 1, 1])
        edit_btn.bind(on_release=self.edit_task)
        del_btn = Button(text='Delete', size_hint_x=None, width=70, height=40, font_size=16, background_color=[16/255, 185/255, 129/255, 1], color=[1, 1, 1, 1])
        del_btn.bind(on_release=self.delete_task)
        btn_row1.add_widget(edit_btn)
        btn_row1.add_widget(del_btn)
        right_col.add_widget(btn_row1)
        row.add_widget(left_col)
        row.add_widget(right_col)
        self.add_widget(row)

    def on_status_change(self, spinner, value):
        self.status = value
        self.build_task()
        self.app_ref.refresh_task_list()

    def edit_task(self, instance):
        self.app_ref.open_edit_popup(self)

    def delete_task(self, instance):
        self.app_ref.delete_task(self)

    # No longer needed: status is managed by spinner


class ToDoApp(App):
    def save_all_tasks(self):
        # Save all tasks to storage as dicts
        task_dicts = []
        for t in self.tasks:
            task_dicts.append({
                'title': t.title,
                'description': t.description,
                'due_date': t.due_date,
                'status': t.status
            })
        self.storage.save_tasks(task_dicts)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = TaskStorage()
        self.tasks = []
        self.filter_status = "All"

       
    def add_task(self, instance):
        title = self.title_input.text.strip()
        desc = self.desc_input.text.strip()
        due = self.due_input.text.strip()
        due_date = ""
        if due:
            try:
                due_dt = datetime.strptime(due, "%Y-%m-%d").date()
                if due_dt < date.today():
                    self.show_alert("Due date cannot be in the past.")
                    return
                due_date = due
            except Exception:
                self.show_alert("Invalid due date format. Use YYYY-MM-DD.")
                return
        if not title:
            return
        task = Task(title, desc, self, due_date=due_date)
        self.tasks.append(task)
        self.save_all_tasks()
        self.refresh_task_list()
        self.title_input.text = ''
        self.desc_input.text = ''
        self.due_input.text = ''

    def build(self):
        # Load tasks from storage
        self.tasks = []
        for t in self.storage.load_tasks():
            self.tasks.append(Task(
                t.get('title', ''),
                t.get('description', ''),
                self,
                due_date=t.get('due_date', ''),
                status=t.get('status', 'Pending')
            ))

        root = BoxLayout(orientation='vertical', padding=[20, 40, 20, 40], spacing=20)
        input_box = BoxLayout(orientation='vertical', size_hint_y=None, height=240, spacing=10, padding=[10, 20, 10, 20])
        self.title_input = TextInput(hint_text='Task Title', multiline=False, size_hint_y=None, height=40, padding=[10, 10, 10, 10], background_color=[243/255, 244/255, 246/255, 1], foreground_color=[31/255, 41/255, 55/255, 1], size_hint_x=1)
        self.desc_input = TextInput(hint_text='Description/Notes (optional)', multiline=True, size_hint_y=None, height=60, padding=[10, 10, 10, 10], background_color=[243/255, 244/255, 246/255, 1], foreground_color=[31/255, 41/255, 55/255, 1], size_hint_x=1)
        self.due_input = TextInput(hint_text='Due Date (YYYY-MM-DD)', multiline=False, size_hint_y=None, height=40, padding=[10, 10, 10, 10], background_color=[243/255, 244/255, 246/255, 1], foreground_color=[31/255, 41/255, 55/255, 1], size_hint_x=1)
        add_btn = Button(
            text='Add Task',
            size_hint_y=None,
            height=50,
            size_hint_x=1,
            padding=[20, 20, 20, 20],  # 20px inner padding on all sides
            background_color=[59/255, 130/255, 246/255, 1],
            color=[1, 1, 1, 1]
        )
        add_btn.bind(on_release=self.add_task)
        input_box.add_widget(self.title_input)
        input_box.add_widget(self.desc_input)
        input_box.add_widget(self.due_input)
        input_box.add_widget(add_btn)
        root.add_widget(input_box)

        self.task_list_layout = GridLayout(cols=1, spacing=10, size_hint_y=None, size_hint_x=1)
        self.task_list_layout.bind(minimum_height=self.task_list_layout.setter('height'))
        self.task_list_layout.height = self.task_list_layout.minimum_height
        self.scroll = ScrollView(size_hint=(1, 1))
        self.scroll.add_widget(self.task_list_layout)
        root.add_widget(self.scroll)

        # Show loaded tasks immediately
        self.refresh_task_list()

        # Start reminder system
        from kivy.clock import Clock
        Clock.schedule_interval(self.check_overdue_tasks, 60)  # every 60 seconds

        return root

    def refresh_task_list(self):
        self.task_list_layout.clear_widgets()
        # Sort: In-Progress at top, Pending in middle, Completed at bottom
        def sort_key(task):
            if task.status == "In-Progress":
                return (0, )
            elif task.status == "Pending":
                return (1, )
            elif task.status == "Completed":
                return (2, )
            return (3, )
        sorted_tasks = sorted(self.tasks, key=sort_key)
        for task in sorted_tasks:
            task.size_hint_x = 1
            task.build_task()
            self.task_list_layout.add_widget(task)
        self.task_list_layout.height = self.task_list_layout.minimum_height

    def open_edit_popup(self, task):
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        title_input = TextInput(text=task.title, multiline=False, size_hint_y=None, height=40)
        desc_input = TextInput(text=task.description, multiline=True, size_hint_y=None, height=60)
        due_input = TextInput(text=task.due_date, multiline=False, size_hint_y=None, height=40, hint_text='Due Date (YYYY-MM-DD)')
        btn_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=30, spacing=5)
        save_btn = Button(text='Save')
        cancel_btn = Button(text='Cancel')
        btn_box.add_widget(save_btn)
        btn_box.add_widget(cancel_btn)
        popup_layout.add_widget(Label(text='Edit Task', size_hint_y=None, height=30))
        popup_layout.add_widget(title_input)
        popup_layout.add_widget(desc_input)
        popup_layout.add_widget(due_input)
        popup_layout.add_widget(btn_box)
        popup = Popup(title='Edit Task', content=popup_layout, size_hint=(0.7, 0.6))

        def save_changes(instance):
            new_title = title_input.text.strip()
            new_desc = desc_input.text.strip()
            new_due = due_input.text.strip()
            due_date = ""
            if new_due:
                try:
                    due_dt = datetime.strptime(new_due, "%Y-%m-%d").date()
                    if due_dt < date.today():
                        self.show_alert("Due date cannot be in the past.")
                        return
                    due_date = new_due
                except Exception:
                    self.show_alert("Invalid due date format. Use YYYY-MM-DD.")
                    return
            if not new_title:
                self.show_alert("Title cannot be empty.")
                return
            task.title = new_title
            task.description = new_desc
            task.due_date = due_date
            task.completed = False
            task.build_task()
            self.save_all_tasks()
            self.refresh_task_list()
            popup.dismiss()

        def cancel_changes(instance):
            popup.dismiss()

        save_btn.bind(on_release=save_changes)
        cancel_btn.bind(on_release=cancel_changes)
        popup.open()

    def delete_task(self, task):
        if task in self.tasks:
            self.tasks.remove(task)
            self.save_all_tasks()
            self.refresh_task_list()

    def show_alert(self, message):
        popup = Popup(title='Alert', content=Label(text=message), size_hint=(0.5, 0.3))
        popup.open()

    def check_overdue_tasks(self, dt):
        overdue = [task for task in self.tasks if task.is_overdue() and not task.completed]
        if overdue:
            msg = "Overdue tasks:\n" + "\n".join(f"- {task.title} (Due: {task.due_date})" for task in overdue)
            popup = Popup(title='Overdue Tasks', content=Label(text=msg), size_hint=(0.5, 0.4))
            popup.open()

if __name__ == '__main__':
    ToDoApp().run()