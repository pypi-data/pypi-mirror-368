"""Shell completion commands for Gira."""

import os
from pathlib import Path
from typing import Optional

import typer
from gira.utils.console import console
def install_completion(
    shell: str = typer.Argument(..., help="Shell type: bash, zsh, fish"),
    path: str = typer.Option(None, "--path", help="Custom installation path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed path selection process")
) -> None:
    """Install shell completion for Gira.
    
    ⚠️  DEPRECATION WARNING: This custom completion system is deprecated.
    
    The recommended approach is to use Typer's built-in completion system:
        gira --install-completion
    
    This provides better integration and automatic ticket/epic/sprint ID completion.
    """

    # Show deprecation warning
    console.print("[yellow]⚠️  WARNING:[/yellow] This completion system is deprecated.")
    console.print("[yellow]The recommended approach is:[/yellow] [cyan]gira --install-completion[/cyan]")  
    console.print("[dim]This will install Typer's built-in completion with dynamic ID completion.[/dim]\n")

    # Generate completion script
    completion_script = _generate_completion_script(shell)

    if not completion_script:
        console.print(f"[red]Error:[/red] Unsupported shell: {shell}")
        raise typer.Exit(1)

    # Determine installation path
    if path:
        install_path = Path(path)
        if verbose:
            console.print(f"[dim]Using custom path: {install_path}[/dim]")
    else:
        install_path = _get_default_completion_path(shell, verbose=verbose)

    if not install_path:
        console.print(f"[red]Error:[/red] Could not determine completion path for {shell}")
        console.print("Use --path to specify a custom path")
        raise typer.Exit(1)

    # Create directory if it doesn't exist
    install_path.parent.mkdir(parents=True, exist_ok=True)

    # Write completion script
    try:
        install_path.write_text(completion_script)
        console.print(f"[green]Success:[/green] Completion installed to {install_path}")

        # Show instructions
        _show_installation_instructions(shell, install_path)

    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to install completion: {e}")
        raise typer.Exit(1)


def show_completion(
    shell: str = typer.Argument(..., help="Shell type: bash, zsh, fish")
) -> None:
    """Show completion script for manual installation.
    
    ⚠️  DEPRECATION WARNING: This custom completion system is deprecated.
    
    Use 'gira --show-completion' instead for Typer's built-in completion.
    """
    
    # Show deprecation warning
    console.print("[yellow]⚠️  WARNING:[/yellow] This completion system is deprecated.")
    console.print("[yellow]Use instead:[/yellow] [cyan]gira --show-completion[/cyan]")  
    console.print("[dim]This will show Typer's built-in completion with dynamic ID completion.[/dim]\n")
    
    completion_script = _generate_completion_script(shell)

    if not completion_script:
        console.print(f"[red]Error:[/red] Unsupported shell: {shell}")
        raise typer.Exit(1)

    console.print(completion_script)


def _generate_completion_script(shell: str) -> str:
    """Generate completion script for the specified shell."""
    if shell == "bash":
        return _generate_bash_completion()
    elif shell == "zsh":
        return _generate_zsh_completion()
    elif shell == "fish":
        return _generate_fish_completion()
    else:
        return ""


def _generate_bash_completion() -> str:
    """Generate bash completion script."""
    return '''
# Gira bash completion

_gira_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Main commands
    if [ ${COMP_CWORD} -eq 1 ]; then
        opts="init version board ticket epic sprint comment team config archive completion query query-save query-list query-run context workflow attachment storage"
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    fi
    
    # Option completion
    case "${prev}" in
        -a|--assignee)
            # Complete with team members if available
            local team_members=$(gira config get user.email 2>/dev/null | grep -v "^$" || echo "")
            COMPREPLY=( $(compgen -W "${team_members}" -- ${cur}) )
            return 0
            ;;
        -s|--status)
            opts="backlog todo in_progress review done"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        -t|--type)
            opts="story task bug epic feature subtask"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        -p|--priority)
            opts="low medium high critical"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        -f|--format)
            opts="table json yaml csv tsv text ids"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        -q|--query)
            # Query field completion and saved queries
            local query_fields="id title description status priority type assignee reporter epic_id parent_id sprint_id blocked_by blocks labels comment_count attachment_count due_date story_points created_at updated_at"
            local query_operators=": != ~ !~ > >= < <= contains starts_with ends_with matches in not_in is_null is_not_null empty not_empty"
            local query_functions="me() today() days_ago() weeks_ago() months_ago() start_of_week() end_of_week() start_of_month() end_of_month()"
            local query_keywords="AND OR NOT"
            
            # Get saved query names
            local saved_queries=""
            if command -v gira >/dev/null 2>&1; then
                saved_queries=$(gira query-list --format json 2>/dev/null | jq -r '.[].name' 2>/dev/null | sed 's/^/@/')
            fi
            
            local all_completions="${query_fields} ${query_operators} ${query_functions} ${query_keywords} ${saved_queries}"
            COMPREPLY=( $(compgen -W "${all_completions}" -- ${cur}) )
            return 0
            ;;
    esac
    
    # Subcommands
    case "${COMP_WORDS[1]}" in
        ticket)
            if [ ${COMP_CWORD} -eq 2 ]; then
                opts="create list show update move tree add-dep remove-dep deps order delete"
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            elif [ ${COMP_CWORD} -eq 3 ] && [[ "${COMP_WORDS[2]}" =~ ^(show|update|move|tree|deps|delete)$ ]]; then
                # Complete with ticket IDs
                local tickets=$(gira ticket list --ids-only 2>/dev/null || echo "")
                COMPREPLY=( $(compgen -W "${tickets}" -- ${cur}) )
            elif [ ${COMP_CWORD} -eq 3 ] && [[ "${COMP_WORDS[2]}" =~ ^(add-dep|remove-dep|order)$ ]]; then
                # Complete with ticket IDs
                local tickets=$(gira ticket list --ids-only 2>/dev/null || echo "")
                COMPREPLY=( $(compgen -W "${tickets}" -- ${cur}) )
            elif [[ "${cur}" == -* ]]; then
                # Command-specific options
                case "${COMP_WORDS[2]}" in
                    create)
                        opts="-d --description -t --type -p --priority -s --status -a --assignee --strict --epic --parent -l --labels"
                        ;;
                    show)
                        opts="-f --format"
                        ;;
                    update)
                        opts="--title -d --description -t --type -p --priority -s --status -a --assignee --strict --epic --add-label --remove-label"
                        ;;
                    list)
                        opts="-s --status -t --type -p --priority -a --assignee --mine --unassigned --epic -l --labels --search --search-in --exact-match --regex-search --case-sensitive-search --sort --reverse --limit --include-archived -q --query -f --format"
                        ;;
                    move)
                        opts="-f --force -p --position"
                        ;;
                    delete)
                        opts="-f --force -p --permanent -o --output"
                        ;;
                esac
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            fi
            ;;
        epic)
            if [ ${COMP_CWORD} -eq 2 ]; then
                opts="create list show update delete"
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            elif [ ${COMP_CWORD} -eq 3 ] && [[ "${COMP_WORDS[2]}" =~ ^(show|update|delete)$ ]]; then
                # Complete with epic IDs
                local epics=$(gira epic list --format json 2>/dev/null | jq -r '.[].id' 2>/dev/null || echo "")
                COMPREPLY=( $(compgen -W "${epics}" -- ${cur}) )
            elif [[ "${cur}" == -* ]]; then
                # Command-specific options
                case "${COMP_WORDS[2]}" in
                    create)
                        opts="-d --description -s --status -a --assignee --start-date --end-date"
                        ;;
                    show)
                        opts="-f --format"
                        ;;
                    update)
                        opts="--title -d --description -s --status -a --assignee --start-date --end-date --add-ticket --remove-ticket"
                        ;;
                    list)
                        opts="-s --status -a --assignee --search --search-in --exact-match --regex-search --case-sensitive-search -q --query -f --format"
                        ;;
                    delete)
                        opts="-f --force -p --permanent -o --output"
                        ;;
                esac
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            fi
            ;;
        sprint)
            if [ ${COMP_CWORD} -eq 2 ]; then
                opts="create list show update start close delete"
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            elif [ ${COMP_CWORD} -eq 3 ] && [[ "${COMP_WORDS[2]}" =~ ^(show|update|start|close|delete)$ ]]; then
                # Complete with sprint IDs
                local sprints=$(gira sprint list --format json 2>/dev/null | jq -r '.[].id' 2>/dev/null || echo "")
                COMPREPLY=( $(compgen -W "${sprints}" -- ${cur}) )
            elif [[ "${cur}" == -* ]]; then
                # Command-specific options
                case "${COMP_WORDS[2]}" in
                    create)
                        opts="-s --start-date -d --duration -e --end-date --goal"
                        ;;
                    update)
                        opts="--name --goal -s --status --start-date --end-date --add-ticket --remove-ticket"
                        ;;
                    list)
                        opts="--active --completed --search --search-in --exact-match --regex-search --case-sensitive-search -q --query -f --format"
                        ;;
                    show)
                        opts="-f --format"
                        ;;
                    close)
                        opts="--retrospective --no-retrospective"
                        ;;
                    delete)
                        opts="-f --force -p --permanent -o --output"
                        ;;
                esac
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            fi
            ;;
        metrics)
            if [ ${COMP_CWORD} -eq 2 ]; then
                opts="velocity trends duration"
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            elif [[ "${cur}" == -* ]]; then
                # Command-specific options
                case "${COMP_WORDS[2]}" in
                    velocity)
                        opts="-n --limit -f --format --all --help"
                        ;;
                    trends)
                        opts="-d --days -f --format -t --type -p --priority -a --assignee -e --epic --weekly --help"
                        ;;
                    duration)
                        opts="-d --days -f --format -t --type -p --priority --help"
                        ;;
                esac
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            fi
            ;;
        comment)
            if [ ${COMP_CWORD} -eq 2 ]; then
                opts="add list delete"
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            elif [ ${COMP_CWORD} -eq 3 ]; then
                # Complete with ticket IDs
                local tickets=$(gira ticket list --ids-only 2>/dev/null || echo "")
                COMPREPLY=( $(compgen -W "${tickets}" -- ${cur}) )
            elif [ ${COMP_CWORD} -eq 4 ] && [[ "${COMP_WORDS[2]}" == "delete" ]]; then
                # For delete command, need comment ID after ticket ID
                # This would ideally list comment IDs for the specific ticket
                # but that's complex, so we'll just provide option flags
                if [[ "${cur}" == -* ]]; then
                    opts="-f --force -o --output"
                    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
                fi
            elif [[ "${cur}" == -* ]]; then
                # Command-specific options
                case "${COMP_WORDS[2]}" in
                    add)
                        opts="-c --content -e --editor"
                        ;;
                    list)
                        opts="-l --limit -r --reverse -f --format"
                        ;;
                    delete)
                        opts="-f --force -o --output"
                        ;;
                esac
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            fi
            ;;
        config)
            if [ ${COMP_CWORD} -eq 2 ]; then
                opts="set get reset"
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            elif [[ "${cur}" == -* ]]; then
                # Command-specific options
                case "${COMP_WORDS[2]}" in
                    set)
                        opts="-g --global"
                        ;;
                    get)
                        opts="-l --list"
                        ;;
                    reset)
                        opts="-f --force"
                        ;;
                esac
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            fi
            ;;
        archive)
            if [ ${COMP_CWORD} -eq 2 ]; then
                opts="ticket done old list restore"
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            elif [ ${COMP_CWORD} -eq 3 ] && [[ "${COMP_WORDS[2]}" =~ ^(ticket|restore)$ ]]; then
                # Complete with ticket IDs
                local tickets=$(gira ticket list --ids-only --include-archived 2>/dev/null || echo "")
                COMPREPLY=( $(compgen -W "${tickets}" -- ${cur}) )
            elif [[ "${cur}" == -* ]]; then
                # Command-specific options
                case "${COMP_WORDS[2]}" in
                    ticket|done)
                        opts="-f --force --dry-run"
                        ;;
                    old)
                        opts="-d --days -s --status --dry-run -f --force"
                        ;;
                    list)
                        opts="--month --search --search-in --limit --stats -f --format"
                        ;;
                    restore)
                        opts="-s --status -f --force"
                        ;;
                esac
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            fi
            ;;
        team)
            if [ ${COMP_CWORD} -eq 2 ]; then
                opts="list add remove discover"
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            elif [[ "${cur}" == -* ]]; then
                # Command-specific options
                case "${COMP_WORDS[2]}" in
                    list)
                        opts="-r --role --active-only -f --format"
                        ;;
                    add)
                        opts="-n --name -u --username -r --role -a --alias -i --interactive"
                        ;;
                    remove)
                        opts="-f --force"
                        ;;
                    discover)
                        opts="-l --limit --add-all --dry-run"
                        ;;
                esac
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            fi
            ;;
        query)
            if [ ${COMP_CWORD} -eq 2 ]; then
                # Complete with saved query names and query syntax
                local saved_queries=""
                if command -v gira >/dev/null 2>&1; then
                    saved_queries=$(gira query-list --format json 2>/dev/null | jq -r '.[].name' 2>/dev/null | sed 's/^/@/')
                fi
                local query_fields="id title description status priority type assignee reporter"
                local all_completions="${saved_queries} ${query_fields}"
                COMPREPLY=( $(compgen -W "${all_completions}" -- ${cur}) )
            elif [[ "${cur}" == -* ]]; then
                opts="-e --entity -f --format -l --limit -o --offset -s --sort --no-header -v --verbose"
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            fi
            ;;
        query-save)
            if [[ "${cur}" == -* ]]; then
                opts="-d --description -e --entity -f --force"
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            fi
            ;;
        query-list)
            if [[ "${cur}" == -* ]]; then
                opts="-e --entity -v --verbose"
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            fi
            ;;
        query-run)
            if [ ${COMP_CWORD} -eq 2 ]; then
                # Complete with saved query names
                local saved_queries=""
                if command -v gira >/dev/null 2>&1; then
                    saved_queries=$(gira query-list --format json 2>/dev/null | jq -r '.[].name' 2>/dev/null)
                fi
                COMPREPLY=( $(compgen -W "${saved_queries}" -- ${cur}) )
            elif [[ "${cur}" == -* ]]; then
                opts="-f --format -l --limit -o --offset -s --sort --no-header -v --verbose"
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            fi
            ;;
        context)
            if [ ${COMP_CWORD} -eq 2 ]; then
                # Complete with ticket IDs
                local tickets=$(gira ticket list --ids-only 2>/dev/null || echo "")
                COMPREPLY=( $(compgen -W "${tickets}" -- ${cur}) )
            elif [[ "${cur}" == -* ]]; then
                opts="-o --output -f --fields --include-archived"
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            fi
            ;;
        workflow)
            if [ ${COMP_CWORD} -eq 2 ]; then
                # Complete with ticket IDs
                local tickets=$(gira ticket list --ids-only 2>/dev/null || echo "")
                COMPREPLY=( $(compgen -W "${tickets}" -- ${cur}) )
            elif [[ "${cur}" == -* ]]; then
                opts="-c --check -o --output"
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            elif [ "${prev}" = "-c" ] || [ "${prev}" = "--check" ]; then
                # Complete with status options
                opts="backlog todo in_progress review done"
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            fi
            ;;
        completion)
            if [ ${COMP_CWORD} -eq 2 ]; then
                opts="install show"
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            elif [ ${COMP_CWORD} -eq 3 ]; then
                opts="bash zsh fish"
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            elif [[ "${cur}" == -* ]]; then
                # Command-specific options
                case "${COMP_WORDS[2]}" in
                    install)
                        opts="--path -v --verbose"
                        ;;
                esac
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            fi
            ;;
        attachment)
            if [ ${COMP_CWORD} -eq 2 ]; then
                opts="add list open remove download cat"
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            elif [ ${COMP_CWORD} -eq 3 ] && [[ "${COMP_WORDS[2]}" =~ ^(add|list|open|remove|download|cat)$ ]]; then
                # Complete with ticket/epic IDs
                local tickets=$(gira ticket list --ids-only 2>/dev/null || echo "")
                local epics=$(gira epic list --format json 2>/dev/null | jq -r '.[].id' 2>/dev/null | sed 's/^/EPIC-/' || echo "")
                COMPREPLY=( $(compgen -W "${tickets} ${epics}" -- ${cur}) )
            elif [ ${COMP_CWORD} -ge 4 ] && [[ "${COMP_WORDS[2]}" =~ ^(add|download|open|remove|cat)$ ]]; then
                # File path completion for add command
                if [[ "${COMP_WORDS[2]}" == "add" ]]; then
                    # Enable file/directory completion
                    compopt -o default
                    COMPREPLY=()
                elif [[ "${COMP_WORDS[2]}" =~ ^(download|open|remove|cat)$ ]]; then
                    # Complete with attachment filenames for entity
                    local entity_id="${COMP_WORDS[3]}"
                    local attachments=$(gira attachment list "${entity_id}" --format json 2>/dev/null | jq -r '.[].file_name' 2>/dev/null || echo "")
                    COMPREPLY=( $(compgen -W "${attachments}" -- ${cur}) )
                fi
            elif [[ "${cur}" == -* ]]; then
                # Command-specific options
                case "${COMP_WORDS[2]}" in
                    add)
                        opts="-n --note -t --type --commit --no-commit -u --user -i --include -e --exclude"
                        ;;
                    list)
                        opts="-v --verbose -f --format"
                        ;;
                    open)
                        opts=""
                        ;;
                    remove)
                        opts="-t --type -r --delete-remote -n --dry-run -f --force --no-commit"
                        ;;
                    download)
                        opts="-t --type -o --output -q --quiet -f --force -a --all"
                        ;;
                    cat)
                        opts="-t --type"
                        ;;
                esac
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            fi
            ;;
        storage)
            if [ ${COMP_CWORD} -eq 2 ]; then
                opts="configure test-connection show-config"
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            elif [[ "${cur}" == -* ]]; then
                # Command-specific options
                case "${COMP_WORDS[2]}" in
                    configure)
                        opts="-p --provider -b --bucket -r --region --base-path --interactive"
                        ;;
                    test-connection)
                        opts=""
                        ;;
                    show-config)
                        opts="--show-credentials"
                        ;;
                esac
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            elif [ "${prev}" = "-p" ] || [ "${prev}" = "--provider" ]; then
                # Complete with provider names
                opts="s3 gcs azure r2 b2"
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            fi
            ;;
    esac
}

complete -F _gira_completion gira
'''


def _generate_zsh_completion() -> str:
    """Generate zsh completion script."""
    return '''
#compdef gira

_gira() {
    local context state line
    
    _arguments \\
        '1: :->command' \\
        '*: :->args'
    
    case $state in
        command)
            _values "gira commands" \\
                "init[Initialize a new Gira project]" \\
                "version[Show version information]" \\
                "board[Display kanban board]" \\
                "ticket[Ticket operations]" \\
                "epic[Epic operations]" \\
                "sprint[Sprint operations]" \\
                "metrics[Project metrics and analytics]" \\
                "comment[Comment operations]" \\
                "team[Team management]" \\
                "config[Configuration management]" \\
                "archive[Archive management]" \\
                "completion[Shell completion management]" \\
                "query[Execute query across entities]" \\
                "query-save[Save a query for later use]" \\
                "query-list[List saved queries]" \\
                "query-run[Run a saved query]" \\
                "context[Show comprehensive ticket context]" \\
                "attachment[Attachment operations]" \\
                "storage[Storage configuration]"
            ;;
        args)
            case $words[2] in
                ticket)
                    if (( CURRENT == 3 )); then
                        _values "ticket commands" \\
                            "create[Create a new ticket]" \\
                            "list[List tickets]" \\
                            "show[Show ticket details]" \\
                            "update[Update ticket]" \\
                            "move[Move ticket to different status]" \\
                            "tree[Display ticket hierarchy tree]" \\
                            "add-dep[Add dependency to ticket]" \\
                            "remove-dep[Remove dependency from ticket]" \\
                            "deps[Show ticket dependencies]" \\
                            "order[Set ticket order in column]" \
                            "delete[Delete or archive a ticket]"
                    elif (( CURRENT == 4 )) && [[ $words[3] =~ ^(show|update|move|tree|deps|add-dep|remove-dep|order|delete)$ ]]; then
                        # Complete with ticket IDs
                        local tickets=(${(f)"$(gira ticket list --ids-only 2>/dev/null)"})
                        _describe "ticket IDs" tickets
                    fi
                    ;;
                epic)
                    if (( CURRENT == 3 )); then
                        _values "epic commands" \\
                            "create[Create a new epic]" \\
                            "list[List epics]" \\
                            "show[Show epic details]" \\
                            "update[Update epic]" \
                            "delete[Delete or archive an epic]"
                    elif (( CURRENT == 4 )) && [[ $words[3] =~ ^(show|update|delete)$ ]]; then
                        # Complete with epic IDs
                        local epics=(${(f)"$(gira epic list --format json 2>/dev/null | jq -r '.[].id' 2>/dev/null)"})
                        _describe "epic IDs" epics
                    fi
                    ;;
                sprint)
                    if (( CURRENT == 3 )); then
                        _values "sprint commands" \\
                            "create[Create a new sprint]" \\
                            "list[List sprints]" \\
                            "show[Show sprint details]" \\
                            "update[Update sprint]" \\
                            "start[Start sprint]" \\
                            "close[Close sprint]" \
                            "delete[Delete or archive a sprint]"
                    elif (( CURRENT == 4 )) && [[ $words[3] =~ ^(show|update|start|close|delete)$ ]]; then
                        # Complete with sprint IDs
                        local sprints=(${(f)"$(gira sprint list --format json 2>/dev/null | jq -r '.[].id' 2>/dev/null)"})
                        _describe "sprint IDs" sprints
                    fi
                    ;;
                metrics)
                    if (( CURRENT == 3 )); then
                        _values "metrics commands" \\
                            "velocity[Display team velocity trends]" \\
                            "trends[Track ticket counts and trends over time]" \\
                            "duration[Analyze time tickets spend in each status]"
                    fi
                    ;;
                comment)
                    if (( CURRENT == 3 )); then
                        _values "comment commands" \\
                            "add[Add comment to ticket]" \\
                            "list[List ticket comments]" \
                            "delete[Delete a comment]"
                    elif (( CURRENT == 4 )); then
                        # Complete with ticket IDs
                        local tickets=(${(f)"$(gira ticket list --ids-only 2>/dev/null)"})
                        _describe "ticket IDs" tickets
                    fi
                    ;;
                config)
                    if (( CURRENT == 3 )); then
                        _values "config commands" \\
                            "set[Set configuration value]" \\
                            "get[Get configuration value]" \\
                            "reset[Reset configuration to defaults]"
                    fi
                    ;;
                archive)
                    if (( CURRENT == 3 )); then
                        _values "archive commands" \\
                            "ticket[Archive a single ticket]" \\
                            "done[Archive all done tickets]" \\
                            "old[Archive old tickets]" \\
                            "list[List archived tickets]" \\
                            "restore[Restore archived ticket]"
                    elif (( CURRENT == 4 )) && [[ $words[3] =~ ^(ticket|restore)$ ]]; then
                        # Complete with ticket IDs (including archived)
                        local tickets=(${(f)"$(gira ticket list --ids-only --include-archived 2>/dev/null)"})
                        _describe "ticket IDs" tickets
                    fi
                    ;;
                team)
                    if (( CURRENT == 3 )); then
                        _values "team commands" \\
                            "list[List team members]" \\
                            "add[Add team member]" \\
                            "remove[Remove team member]" \\
                            "discover[Discover team members from Git history]"
                    fi
                    ;;
                completion)
                    if (( CURRENT == 3 )); then
                        _values "completion commands" \\
                            "install[Install shell completion]" \\
                            "show[Show completion script]"
                    elif (( CURRENT == 4 )); then
                        _values "shell type" \\
                            "bash" \\
                            "zsh" \\
                            "fish"
                    fi
                    ;;
                attachment)
                    if (( CURRENT == 3 )); then
                        _values "attachment commands" \\
                            "add[Add attachment(s) to entity]" \\
                            "list[List entity attachments]" \\
                            "open[Open attachment with default app]" \\
                            "remove[Remove attachment(s)]" \\
                            "download[Download attachment(s)]" \\
                            "cat[Stream text file content]"
                    elif (( CURRENT == 4 )); then
                        # Complete with ticket/epic IDs
                        local tickets=(${(f)"$(gira ticket list --ids-only 2>/dev/null)"})
                        local epics=(${(f)"$(gira epic list --format json 2>/dev/null | jq -r '.[].id' 2>/dev/null | sed 's/^/EPIC-/')"})
                        _describe "entity IDs" tickets epics
                    elif (( CURRENT >= 5 )) && [[ $words[3] == "add" ]]; then
                        # File completion for add command
                        _files
                    elif (( CURRENT >= 5 )) && [[ $words[3] =~ ^(download|open|remove|cat)$ ]]; then
                        # Complete with attachment filenames
                        local entity_id=$words[4]
                        local attachments=(${(f)"$(gira attachment list $entity_id --format json 2>/dev/null | jq -r '.[].file_name' 2>/dev/null)"})
                        _describe "attachment files" attachments
                    fi
                    ;;
                storage)
                    if (( CURRENT == 3 )); then
                        _values "storage commands" \\
                            "configure[Configure storage provider]" \\
                            "test-connection[Test storage connection]" \\
                            "show-config[Show storage configuration]"
                    elif [[ $words[3] == "configure" ]] && [[ $words[CURRENT-1] =~ ^(-p|--provider)$ ]]; then
                        _values "storage providers" \\
                            "s3[Amazon S3]" \\
                            "gcs[Google Cloud Storage]" \\
                            "azure[Azure Blob Storage]" \\
                            "r2[Cloudflare R2]" \\
                            "b2[Backblaze B2]"
                    fi
                    ;;
            esac
            ;;
    esac
}

_gira
'''


def _generate_fish_completion() -> str:
    """Generate fish completion script."""
    return '''
# Gira completions for fish

# Main commands
complete -c gira -f -n "__fish_use_subcommand" -a "init" -d "Initialize a new Gira project"
complete -c gira -f -n "__fish_use_subcommand" -a "version" -d "Show version information"
complete -c gira -f -n "__fish_use_subcommand" -a "board" -d "Display kanban board"
complete -c gira -f -n "__fish_use_subcommand" -a "ticket" -d "Ticket operations"
complete -c gira -f -n "__fish_use_subcommand" -a "epic" -d "Epic operations"
complete -c gira -f -n "__fish_use_subcommand" -a "sprint" -d "Sprint operations"
complete -c gira -f -n "__fish_use_subcommand" -a "comment" -d "Comment operations"
complete -c gira -f -n "__fish_use_subcommand" -a "team" -d "Team management"
complete -c gira -f -n "__fish_use_subcommand" -a "config" -d "Configuration management"
complete -c gira -f -n "__fish_use_subcommand" -a "archive" -d "Archive management"
complete -c gira -f -n "__fish_use_subcommand" -a "completion" -d "Shell completion management"
complete -c gira -f -n "__fish_use_subcommand" -a "query" -d "Execute query across entities"
complete -c gira -f -n "__fish_use_subcommand" -a "query-save" -d "Save a query for later use"
complete -c gira -f -n "__fish_use_subcommand" -a "query-list" -d "List saved queries"
complete -c gira -f -n "__fish_use_subcommand" -a "query-run" -d "Run a saved query"
complete -c gira -f -n "__fish_use_subcommand" -a "context" -d "Show comprehensive ticket context"
complete -c gira -f -n "__fish_use_subcommand" -a "attachment" -d "Attachment operations"
complete -c gira -f -n "__fish_use_subcommand" -a "storage" -d "Storage configuration"

# Ticket subcommands
complete -c gira -f -n "__fish_seen_subcommand_from ticket; and not __fish_seen_subcommand_from create list show update move tree add-dep remove-dep deps order delete" -a "create" -d "Create a new ticket"
complete -c gira -f -n "__fish_seen_subcommand_from ticket; and not __fish_seen_subcommand_from create list show update move tree add-dep remove-dep deps order delete" -a "list" -d "List tickets"
complete -c gira -f -n "__fish_seen_subcommand_from ticket; and not __fish_seen_subcommand_from create list show update move tree add-dep remove-dep deps order delete" -a "show" -d "Show ticket details"
complete -c gira -f -n "__fish_seen_subcommand_from ticket; and not __fish_seen_subcommand_from create list show update move tree add-dep remove-dep deps order delete" -a "update" -d "Update ticket"
complete -c gira -f -n "__fish_seen_subcommand_from ticket; and not __fish_seen_subcommand_from create list show update move tree add-dep remove-dep deps order delete" -a "move" -d "Move ticket to different status"
complete -c gira -f -n "__fish_seen_subcommand_from ticket; and not __fish_seen_subcommand_from create list show update move tree add-dep remove-dep deps order delete" -a "tree" -d "Display ticket hierarchy tree"
complete -c gira -f -n "__fish_seen_subcommand_from ticket; and not __fish_seen_subcommand_from create list show update move tree add-dep remove-dep deps order delete" -a "add-dep" -d "Add dependency to ticket"
complete -c gira -f -n "__fish_seen_subcommand_from ticket; and not __fish_seen_subcommand_from create list show update move tree add-dep remove-dep deps order delete" -a "remove-dep" -d "Remove dependency from ticket"
complete -c gira -f -n "__fish_seen_subcommand_from ticket; and not __fish_seen_subcommand_from create list show update move tree add-dep remove-dep deps order delete" -a "deps" -d "Show ticket dependencies"
complete -c gira -f -n "__fish_seen_subcommand_from ticket; and not __fish_seen_subcommand_from create list show update move tree add-dep remove-dep deps order delete" -a "order" -d "Set ticket order in column"
complete -c gira -f -n "__fish_seen_subcommand_from ticket; and not __fish_seen_subcommand_from create list show update move tree add-dep remove-dep deps order delete" -a "delete" -d "Delete or archive a ticket"

# Epic subcommands
complete -c gira -f -n "__fish_seen_subcommand_from epic; and not __fish_seen_subcommand_from create list show update delete" -a "create" -d "Create a new epic"
complete -c gira -f -n "__fish_seen_subcommand_from epic; and not __fish_seen_subcommand_from create list show update delete" -a "list" -d "List epics"
complete -c gira -f -n "__fish_seen_subcommand_from epic; and not __fish_seen_subcommand_from create list show update delete" -a "show" -d "Show epic details"
complete -c gira -f -n "__fish_seen_subcommand_from epic; and not __fish_seen_subcommand_from create list show update delete" -a "update" -d "Update epic"
complete -c gira -f -n "__fish_seen_subcommand_from epic; and not __fish_seen_subcommand_from create list show update delete" -a "delete" -d "Delete or archive an epic"

# Metrics subcommands
complete -c gira -f -n "__fish_seen_subcommand_from metrics; and not __fish_seen_subcommand_from velocity trends duration" -a "velocity" -d "Display team velocity trends"
complete -c gira -f -n "__fish_seen_subcommand_from metrics; and not __fish_seen_subcommand_from velocity trends duration" -a "trends" -d "Track ticket counts and trends over time"
complete -c gira -f -n "__fish_seen_subcommand_from metrics; and not __fish_seen_subcommand_from velocity trends duration" -a "duration" -d "Analyze time tickets spend in each status"

# Sprint subcommands
complete -c gira -f -n "__fish_seen_subcommand_from sprint; and not __fish_seen_subcommand_from create list show update start close delete" -a "create" -d "Create a new sprint"
complete -c gira -f -n "__fish_seen_subcommand_from sprint; and not __fish_seen_subcommand_from create list show update start close delete" -a "list" -d "List sprints"
complete -c gira -f -n "__fish_seen_subcommand_from sprint; and not __fish_seen_subcommand_from create list show update start close delete" -a "show" -d "Show sprint details"
complete -c gira -f -n "__fish_seen_subcommand_from sprint; and not __fish_seen_subcommand_from create list show update start close delete" -a "update" -d "Update sprint"
complete -c gira -f -n "__fish_seen_subcommand_from sprint; and not __fish_seen_subcommand_from create list show update start close delete" -a "start" -d "Start sprint"
complete -c gira -f -n "__fish_seen_subcommand_from sprint; and not __fish_seen_subcommand_from create list show update start close delete" -a "close" -d "Close sprint"
complete -c gira -f -n "__fish_seen_subcommand_from sprint; and not __fish_seen_subcommand_from create list show update start close delete" -a "delete" -d "Delete or archive a sprint"

# Comment subcommands
complete -c gira -f -n "__fish_seen_subcommand_from comment; and not __fish_seen_subcommand_from add list delete" -a "add" -d "Add comment to ticket"
complete -c gira -f -n "__fish_seen_subcommand_from comment; and not __fish_seen_subcommand_from add list delete" -a "list" -d "List ticket comments"
complete -c gira -f -n "__fish_seen_subcommand_from comment; and not __fish_seen_subcommand_from add list delete" -a "delete" -d "Delete a comment"

# Config subcommands
complete -c gira -f -n "__fish_seen_subcommand_from config; and not __fish_seen_subcommand_from set get reset" -a "set" -d "Set configuration value"
complete -c gira -f -n "__fish_seen_subcommand_from config; and not __fish_seen_subcommand_from set get reset" -a "get" -d "Get configuration value"
complete -c gira -f -n "__fish_seen_subcommand_from config; and not __fish_seen_subcommand_from set get reset" -a "reset" -d "Reset configuration to defaults"

# Archive subcommands
complete -c gira -f -n "__fish_seen_subcommand_from archive; and not __fish_seen_subcommand_from ticket done old list restore" -a "ticket" -d "Archive a single ticket"
complete -c gira -f -n "__fish_seen_subcommand_from archive; and not __fish_seen_subcommand_from ticket done old list restore" -a "done" -d "Archive all done tickets"
complete -c gira -f -n "__fish_seen_subcommand_from archive; and not __fish_seen_subcommand_from ticket done old list restore" -a "old" -d "Archive old tickets"
complete -c gira -f -n "__fish_seen_subcommand_from archive; and not __fish_seen_subcommand_from ticket done old list restore" -a "list" -d "List archived tickets"
complete -c gira -f -n "__fish_seen_subcommand_from archive; and not __fish_seen_subcommand_from ticket done old list restore" -a "restore" -d "Restore archived ticket"

# Team subcommands
complete -c gira -f -n "__fish_seen_subcommand_from team; and not __fish_seen_subcommand_from list add remove discover" -a "list" -d "List team members"
complete -c gira -f -n "__fish_seen_subcommand_from team; and not __fish_seen_subcommand_from list add remove discover" -a "add" -d "Add team member"
complete -c gira -f -n "__fish_seen_subcommand_from team; and not __fish_seen_subcommand_from list add remove discover" -a "remove" -d "Remove team member"
complete -c gira -f -n "__fish_seen_subcommand_from team; and not __fish_seen_subcommand_from list add remove discover" -a "discover" -d "Discover team members from Git history"

# Completion subcommands
complete -c gira -f -n "__fish_seen_subcommand_from completion; and not __fish_seen_subcommand_from install show" -a "install" -d "Install shell completion"
complete -c gira -f -n "__fish_seen_subcommand_from completion; and not __fish_seen_subcommand_from install show" -a "show" -d "Show completion script"

# Shell types for completion command
complete -c gira -f -n "__fish_seen_subcommand_from completion; and __fish_seen_subcommand_from install show" -a "bash zsh fish"

# Attachment subcommands
complete -c gira -f -n "__fish_seen_subcommand_from attachment; and not __fish_seen_subcommand_from add list open remove download cat" -a "add" -d "Add attachment(s) to entity"
complete -c gira -f -n "__fish_seen_subcommand_from attachment; and not __fish_seen_subcommand_from add list open remove download cat" -a "list" -d "List entity attachments"
complete -c gira -f -n "__fish_seen_subcommand_from attachment; and not __fish_seen_subcommand_from add list open remove download cat" -a "open" -d "Open attachment with default app"
complete -c gira -f -n "__fish_seen_subcommand_from attachment; and not __fish_seen_subcommand_from add list open remove download cat" -a "remove" -d "Remove attachment(s)"
complete -c gira -f -n "__fish_seen_subcommand_from attachment; and not __fish_seen_subcommand_from add list open remove download cat" -a "download" -d "Download attachment(s)"
complete -c gira -f -n "__fish_seen_subcommand_from attachment; and not __fish_seen_subcommand_from add list open remove download cat" -a "cat" -d "Stream text file content"

# Storage subcommands
complete -c gira -f -n "__fish_seen_subcommand_from storage; and not __fish_seen_subcommand_from configure test-connection show-config" -a "configure" -d "Configure storage provider"
complete -c gira -f -n "__fish_seen_subcommand_from storage; and not __fish_seen_subcommand_from configure test-connection show-config" -a "test-connection" -d "Test storage connection"
complete -c gira -f -n "__fish_seen_subcommand_from storage; and not __fish_seen_subcommand_from configure test-connection show-config" -a "show-config" -d "Show storage configuration"

# Dynamic completions for IDs
complete -c gira -f -n "__fish_seen_subcommand_from ticket; and __fish_seen_subcommand_from show update move tree add-dep remove-dep deps order delete" -a "(gira ticket list --ids-only 2>/dev/null)" -d "Ticket ID"
complete -c gira -f -n "__fish_seen_subcommand_from epic; and __fish_seen_subcommand_from show update delete" -a "(gira epic list --format json 2>/dev/null | jq -r '.[].id' 2>/dev/null)" -d "Epic ID"
complete -c gira -f -n "__fish_seen_subcommand_from sprint; and __fish_seen_subcommand_from show update start close delete" -a "(gira sprint list --format json 2>/dev/null | jq -r '.[].id' 2>/dev/null)" -d "Sprint ID"
complete -c gira -f -n "__fish_seen_subcommand_from comment" -a "(gira ticket list --ids-only 2>/dev/null)" -d "Ticket ID"
complete -c gira -f -n "__fish_seen_subcommand_from archive; and __fish_seen_subcommand_from ticket restore" -a "(gira ticket list --ids-only --include-archived 2>/dev/null)" -d "Ticket ID"

# Attachment entity ID completions
complete -c gira -f -n "__fish_seen_subcommand_from attachment; and __fish_seen_subcommand_from add list open remove download cat" -a "(gira ticket list --ids-only 2>/dev/null; gira epic list --format json 2>/dev/null | jq -r '.[].id' 2>/dev/null | sed 's/^/EPIC-/')" -d "Entity ID"

# Storage provider completions
complete -c gira -f -n "__fish_seen_subcommand_from storage; and __fish_seen_subcommand_from configure; and __fish_contains_opt -s p provider" -a "s3 gcs azure r2 b2" -d "Storage provider"

# File completions for attachment add
complete -c gira -F -n "__fish_seen_subcommand_from attachment; and __fish_seen_subcommand_from add"

# Attachment filename completions for download/open/remove/cat
complete -c gira -f -n "__fish_seen_subcommand_from attachment; and __fish_seen_subcommand_from download open remove cat; and test (count (commandline -opc)) -ge 4" -a "(gira attachment list (commandline -opc)[4] --format json 2>/dev/null | jq -r '.[].file_name' 2>/dev/null)" -d "Attachment file"
'''


def _get_default_completion_path(shell: str, verbose: bool = False) -> Optional[Path]:
    """Get the default completion installation path for the shell."""
    home = Path.home()

    if shell == "bash":
        # Prefer user directories to avoid permission issues
        user_paths = [
            home / ".local/share/bash-completion/completions/gira",
            home / ".bash_completion.d/gira"
        ]

        # Check if any user directories already exist
        for path in user_paths:
            if path.parent.exists():
                if verbose:
                    console.print(f"[dim]Found existing directory: {path.parent}[/dim]")
                return path

        # Check if we have write access to system directories
        system_paths = [
            Path("/usr/local/etc/bash_completion.d/gira"),
            Path("/etc/bash_completion.d/gira")
        ]

        for path in system_paths:
            if path.parent.exists():
                try:
                    # Test write permission
                    test_file = path.parent / ".gira_test"
                    test_file.touch()
                    test_file.unlink()
                    return path
                except (PermissionError, OSError):
                    continue

        # Default to user directory (will create if needed)
        return home / ".bash_completion.d/gira"

    elif shell == "zsh":
        # Prefer user directories to avoid permission issues
        user_paths = [
            home / ".zfunc/_gira",
            home / ".zsh/completions/_gira"
        ]

        # Check if any user directories already exist
        for path in user_paths:
            if path.parent.exists():
                if verbose:
                    console.print(f"[dim]Found existing directory: {path.parent}[/dim]")
                return path

        # Check if we have write access to system directories
        system_paths = [
            Path("/usr/local/share/zsh/site-functions/_gira"),
            Path("/usr/share/zsh/site-functions/_gira")
        ]

        for path in system_paths:
            if path.parent.exists():
                try:
                    # Test write permission
                    test_file = path.parent / ".gira_test"
                    test_file.touch()
                    test_file.unlink()
                    return path
                except (PermissionError, OSError):
                    continue

        # Default to user directory (will create if needed)
        return home / ".zfunc/_gira"

    elif shell == "fish":
        # Fish completion directory
        config_dir = os.environ.get("XDG_CONFIG_HOME", str(home / ".config"))
        return Path(config_dir) / "fish/completions/gira.fish"

    return None


def _show_installation_instructions(shell: str, install_path: Path) -> None:
    """Show post-installation instructions for the shell."""
    console.print("\n[bold]Next steps:[/bold]")

    if shell == "bash":
        if install_path.parent == Path.home() / ".bash_completion.d":
            console.print("1. Add this to your ~/.bashrc:")
            console.print(f"   [cyan]source {install_path}[/cyan]")
        else:
            console.print("1. Restart your terminal or run:")
            console.print(f"   [cyan]source {install_path}[/cyan]")
        console.print("2. If bash-completion is not working, ensure it's installed:")
        console.print("   [cyan]brew install bash-completion[/cyan] (macOS)")
        console.print("   [cyan]apt install bash-completion[/cyan] (Ubuntu/Debian)")

    elif shell == "zsh":
        if install_path.parent.name in [".zfunc", "completions"]:
            console.print("1. Add the completion directory to your fpath in ~/.zshrc:")
            console.print(f"   [cyan]fpath=({install_path.parent} $fpath)[/cyan]")
            console.print("2. Add autoload if not already present:")
            console.print("   [cyan]autoload -U compinit && compinit[/cyan]")
        else:
            console.print("1. System completion installed. If not working, ensure fpath includes:")
            console.print(f"   [cyan]{install_path.parent}[/cyan]")
        console.print("3. Restart your terminal or run:")
        console.print("   [cyan]exec zsh[/cyan]")

    elif shell == "fish":
        console.print("1. Completions should be available immediately")
        console.print("2. If not working, restart your terminal or run:")
        console.print("   [cyan]source ~/.config/fish/config.fish[/cyan]")

    console.print(f"\n[green]✅ Completion installed to {install_path}[/green]")
