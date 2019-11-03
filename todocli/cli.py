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
    for t in tasks:
        subject = t["subject"]
        status = t["status"]
        folder = t["parentFolderId"]

        click.echo(
            " {:<20}\t{:<20}\t{}".format(
                click.style("ongoing", fg="green"),
                click.style(id2name[folder], fg="blue"),
                subject,
            )
        )


def list_folders():
    folders = auth.list_folders()
    for f in folders:
        print(f)
        click.echo(click.style(f["name"], fg="blue"))
