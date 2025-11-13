## Handeling Error messages
from rich.console import Console

console = Console()

def title(string):
    console.print("\n######",string, "######\n", style="green")

def proc_title(string):
    console.print(">>>>", string, "<<<<", style="blue")

def msg(string):
    console.print("[INFO]", string, style="black")
    
def err_msg(string):
    console.print("[WARN]", string, style="red")