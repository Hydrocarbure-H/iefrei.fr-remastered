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

function load_semester(semester)
{
    const dropbtn = document.querySelector('.dropbtn');

    if (semester === 'all')
    {
        dropbtn.innerHTML = 'Tous les cours <ion-icon name="chevron-down-outline"></ion-icon>';
        window.location.href = "{{ url_for('index') }}";
    }
    else
    {
        dropbtn.innerHTML = 'Semestre ' + semester + ' <ion-icon name="chevron-down-outline"></ion-icon>';
        window.location.href = "{{ url_for('courses_by_semester', semester=semester) }}";
    }
}
