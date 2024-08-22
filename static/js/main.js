/*
    Copy the link of the course to the clipboard
 */
function copy_link(id, title)
{
    const link = window.location.origin + '/courses/' + id;
    navigator.clipboard.writeText(link).then(() =>
    {
        alert('Lien copié pour le cours : ' + title);
    });
}

/*
    Load the semester selected by the user
 */
function load_semester(semester)
{
    window.location.href = window.location.origin + '?semester=' + semester;
}
