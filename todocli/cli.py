import os
import pickle
import click
from todocli import auth


@click.group()
def main():
    pass


@main.command()
@click.option(
    "--all", "-a", "all_", is_flag=True, help="List all tasks including completed ones"
)
@click.option(
    "--filter", "-f", "filter_", default="", help="List tasks from specific folder"
)
@click.option("--folders", is_flag=True, help="List folders")
def list(all_, filter_, folders):
    if folders:
        list_folders()
        return

    if filter_ == "":
        tasks = auth.list_tasks()
    else:
        tasks = auth.list_tasks(filter_)

    (name2id, id2name) = auth.get_folder_mappings()

    # Check if folder names are up-to-date
    for t in tasks:
        folder = t["parentFolderId"]
        if folder not in id2name:
            # Get updated mappings
            auth.list_and_update_folders()
            (name2id, id2name) = auth.get_folder_mappings()
            break

    # Print results
    results = {}
    for idx, t in enumerate(tasks):
        id_ = t["id"]
        subject = t["subject"]
        status = t["status"]
        folder = t["parentFolderId"]

        # This is a bug in Graph API. Deleted tasks/folders are being returned.
        if folder in id2name:
            click.echo(
                " {}   {:<20}\t{:<20}\t{}".format(
                    click.style(str(idx)),
                    click.style("ongoing", fg="green"),
                    click.style(id2name[folder], fg="blue"),
                    subject,
                )
            )
            results[str(idx)] = t

    # Save results for use in other commands
    with open(os.path.join(auth.config_dir, "list_results.pkl"), "wb") as f:
        pickle.dump(results, f)


@main.command()
@click.argument("task_num")
def delete(task_num):
    # Load results from list command
    with open(os.path.join(auth.config_dir, "list_results.pkl"), "rb") as f:
        results = pickle.load(f)

    if task_num not in results:
        click.echo("Task {} does not exist.".format(task_num))
    else:
        task = results[task_num]
        if click.confirm("Delete task? {}".format(task["subject"])):
            ok = auth.delete_task(task["id"])
            if ok:
                click.echo("Done.")
            else:
                click.echo("Oops, something went wrong.")


@main.command()
@click.argument("task_num")
def complete(task_num):
    # Load results from list command
    with open(os.path.join(auth.config_dir, "list_results.pkl"), "rb") as f:
        results = pickle.load(f)

    if task_num not in results:
        click.echo("Task {} does not exist.".format(task_num))
    else:
        task = results[task_num]
        if click.confirm("Mark task as complete? {}".format(task["subject"])):
            ok = auth.complete_task(task["id"])
            if ok:
                click.echo("Done.")
            else:
                click.echo("Oops, something went wrong.")


def list_folders():
    folders = auth.list_and_update_folders()
    for f in folders:
        print(f)
        click.echo(click.style(f["name"], fg="blue"))
