/**
 * Manage the dropdown menu choices for the semesters
 */
document.addEventListener("DOMContentLoaded", function ()
{
        const currentUrl = window.location.href;

        if (currentUrl.includes('/semester/5'))
        {
            setDropbtnText('Semestre 5');
        }
        else if (currentUrl.includes('/semester/6'))
        {
            setDropbtnText('Semestre 6');
        }
        else if (currentUrl.includes('/semester/7'))
        {
            setDropbtnText('Semestre 7');
        }
        else if (currentUrl.includes('/semester/8'))
        {
            setDropbtnText('Semestre 8');
        }
        else
        {
            setDropbtnText('Tous les cours');
        }
});


/**
 * Copy the link of the course to the clipboard
 */
function copy_link(id, title)
{
    const link = window.location.origin + '/courses/' + id;
    navigator.clipboard.writeText(link).then(() =>
    {
        alert('Lien copié pour le cours : ' + title);
    });
}

/**
 * Set the text of the dropdown button
 * @param text
 */
function setDropbtnText(text)
{
    const dropbtn = document.querySelector('.dropbtn');
    dropbtn.innerHTML = text + ' <ion-icon name="chevron-down-outline"></ion-icon>';
}

/**
 * Load the course in the iframe
 * @param courseUrl
 */
function loadCourse(courseUrl)
{

    // If the screen is small (800px), redirect to the course page
    if (window.innerWidth < 800) {
        window.location.href = courseUrl;
    }

    // Update classes for the main divs
    document.getElementById('main_left').classList.remove('full-width');
    document.getElementById('main_left').classList.add('half-width');

    document.getElementById('main_right').classList.remove('hidden');
    document.getElementById('main_right').classList.add('visible');

    // Update the iframe src
    document.getElementById('viewer').src = courseUrl;
}

