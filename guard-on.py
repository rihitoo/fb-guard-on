import os
import requests
import json
import random
import string
import uuid
from rich.console import Console
from rich.panel import Panel

console = Console()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_userid(token):
    url = f"https://graph.facebook.com/me?access_token={token}"
    res = requests.get(url)
    if res.status_code != 200:
        return None, None
    info = res.json()
    return info.get('id'), info.get('name')

def get_token(email, password):
    headers = {
        'authorization': 'OAuth 350685531728|62f8ce9f74b12f84c123cc23437a4a32',
        'x-fb-friendly-name': 'Authenticate',
        'x-fb-connection-type': 'Unknown',
        'accept-encoding': 'gzip, deflate',
        'content-type': 'application/x-www-form-urlencoded',
        'x-fb-http-engine': 'Liger'
    }
    data = {
        'adid': ''.join(random.choices(string.hexdigits, k=16)),
        'format': 'json',
        'device_id': str(uuid.uuid4()),
        'email': email,
        'password': password,
        'generate_analytics_claims': '0',
        'credentials_type': 'password',
        'source': 'login',
        'error_detail_type': 'button_with_disabled',
        'enroll_misauth': 'false',
        'generate_session_cookies': '0',
        'generate_machine_id': '0',
        'fb_api_req_friendly_name': 'authenticate'
    }
    response = requests.post('https://b-graph.facebook.com/auth/login', data=data, headers=headers, timeout=10)
    if response.status_code != 200:
        return None
    result = response.json()
    return result.get('access_token')

def turn_shield(token, enable=True):
    uid, name = get_userid(token)
    if not uid:
        return
    data = {
        'variables': json.dumps({
            '0': {
                'is_shielded': enable,
                'session_id': str(uuid.uuid4()),
                'actor_id': uid,
                'client_mutation_id': str(uuid.uuid4())
            }
        }),
        'method': 'post',
        'doc_id': '1477043292367183'
    }
    headers = {
        'Authorization': f"OAuth {token}"
    }
    url = 'https://graph.facebook.com/graphql'
    res = requests.post(url, json=data, headers=headers)
    if res.status_code != 200:
        console.print(Panel(f"[bold red]Request failed: {res.text}[/bold red]", style='bold red'))
        return

    response_text = res.text
    if '"is_shielded":true' in response_text:
        console.print(Panel('[bold green]✅ Activated Profile Guard[/bold green]', style='bold green'))
    elif '"is_shielded":false' in response_text:
        console.print(Panel('[bold red]❌ Deactivated Profile Guard[/bold red]', style='bold red'))
    else:
        console.print(Panel(f"[bold yellow]⚠ Unexpected response: {response_text}[/bold yellow]", style='bold yellow'))

def guard_on():
    email = console.input('\n[bold yellow]📧 Enter your Facebook Email: [/bold yellow]').strip()
    password = console.input('[bold yellow]🔑 Enter your Facebook Password: [/bold yellow]').strip()
    token = get_token(email, password)
    if not token:
        console.print(Panel('[bold red][!] Failed to retrieve token. Please try again.[/bold red]', style='bold red'))
        return

    uid, name = get_userid(token)
    if not uid:
        console.print(Panel('[bold red][!] Invalid token. Please try again.[/bold red]', style='bold red'))
        return

    console.print(Panel(f"[bold cyan]🔹 Logged in as: {name} (ID: {uid})[/bold cyan]", style='bold cyan'))
    console.print(Panel('[bold green][1] Activate Profile Guard[/bold green]\n[bold red][2] Deactivate Profile Guard[/bold red]\n[bold yellow][3] Back to Main Menu[/bold yellow]'))

    choice = console.input('[bold cyan]Select an option (1/2/3): [/bold cyan]').strip()
    if choice == '1':
        turn_shield(token, True)
    elif choice == '2':
        turn_shield(token, False)
    elif choice == '3':
        return
    else:
        console.print(Panel('[bold red][!] Invalid choice, please try again.[/bold red]', style='bold red'))

    console.input('\n[bold blue]Press Enter to return to the menu...[/bold blue]')
    main()

def main():
    """Main menu."""
    while True:
        clear_screen()
        console.print(Panel('[bold cyan][1] Manage Profile Guard[/bold cyan]\n[bold red][2] Exit[/bold red]',
                            style='bold magenta', title='[bold yellow]🔧 Facebook Guard Tool 🔧'))
        choice = console.input('[bold yellow]Select an option (1/2): [/bold yellow]').strip()
        if choice == '1':
            guard_on()
        elif choice == '2':
            console.print(Panel('[bold blue]👋 Exiting...[/bold blue]', style='bold blue'))
            break
        else:
            console.print(Panel('[bold red][!] Invalid choice, please try again.[/bold red]', style='bold red'))

if __name__ == '__main__':
    main()
