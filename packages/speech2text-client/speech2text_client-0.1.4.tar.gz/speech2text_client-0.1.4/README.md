# Speech2Text Python SDK

Python SDK for API [speech2text.ru](https://speech2text.ru).

## Installation
```
pip install speech2text_client
```

## Usage

```python
from speech2text_client.client import Speech2Text
from speech2text_client.options import RecognizeOptions
from speech2text_client.enums import Formats

api = Speech2Text('YOUR_API_KEY')
options = RecognizeOptions("ru", [1, 2], False)
task = api.recognitions().send_file("test.mp3", options)
result = task.wait().result(Formats.TXT)
print(result)
```

### Show tasks lists

```python
from speech2text_client.client import Speech2Text
from speech2text_client.enums import ListStages

api = Speech2Text('YOUR_API_KEY')
print(api.recognitions().list(limit=10, page=1))  # return last 10 tasks
print(api.recognitions().list(stage=ListStages.COMPLETE.value))  # return completed tasks
print(api.recognitions().list(stage=ListStages.PROCESSING.value))  # return tasks in process
```

### Show tasks information

```python
from speech2text_client.client import Speech2Text

api = Speech2Text('YOUR_API_KEY')
task_id = 'TASK_ID'
task = api.recognitions().task(task_id)
print(f"Id: {task.id()}")
print(f"    Status: {task.status().code} ({task.status().description})")
print(f"    Type: {task.source_type()}")
print(f"    Options:")
print(f"        Language: {task.recognize_options().lang}")
print(f"        Stereo: {task.recognize_options().stereo}")
print(
    f"        Speakers: {task.recognize_options().speakers if isinstance(task.recognize_options().speakers, int) or task.recognize_options().speakers is None else f'from {task.recognize_options().speakers[0]} to {task.recognize_options().speakers[1]}'}")
print(f"    Mime: {task.meta().mime}")
print(f"    File format: {task.meta().format}")
print(f"    Audio format: {task.meta().audio_format}")
```

### Show tasks results

```python
from speech2text_client.client import Speech2Text
from speech2text_client.enums import Formats

api = Speech2Text('YOUR_API_KEY')
task_id = 'TASK_ID'
task = api.recognitions().task(task_id)
print(task.result(Formats.TXT))  # txt
print("=" * 50)
print(task.result(Formats.RAW))  # raw
print("=" * 50)
print(task.result(Formats.SRT))  # srt
print("=" * 50)
print(task.result(Formats.VTT))  # vtt
print("=" * 50)
print(task.result(Formats.JSON))  # json
print("=" * 50)
print(task.result(Formats.XML))  # xml
```

### Work with user and settings

```python
from speech2text_client.client import Speech2Text

api = Speech2Text("YOUR_API_KEY")

print(f"Balance: {api.user().amounts().balance()}")
print(f"Available Minutes: {api.user().amounts().available_minutes()}")
print(f"Used Minutes: {api.user().amounts().used_minutes()}")

print(f"Rate: {api.user().rate().title} ({api.user().rate().minutes} minutes for {api.user().rate().period} day(s))")

print(f"Threads: {api.user().settings().threads()}")
print(f"Auto payment status: {'Yes' if api.user().settings().auto_payments_status() else 'No'}")
print(f"Auto payment ON: {'✅' if api.user().settings().auto_payments_on() else '❌'}")
print(f"Auto payment OFF: {'✅' if api.user().settings().auto_payments_off() else '❌'}")
```