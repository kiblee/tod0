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
    for t in tasks:
        subject = t["subject"]
        status = t["status"]
        folder = t["parentFolderId"]

        # This is a bug in Graph API. Deleted tasks/folders are being returned.
        if folder in id2name:
            click.echo(
                " {:<20}\t{:<20}\t{}".format(
                    click.style("ongoing", fg="green"),
                    click.style(id2name[folder], fg="blue"),
                    subject,
                )
            )


def list_folders():
    folders = auth.list_and_update_folders()
    for f in folders:
        print(f)
        click.echo(click.style(f["name"], fg="blue"))
