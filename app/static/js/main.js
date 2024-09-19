document.getElementById('saveChangesBtn').addEventListener('click', async () => {
    const fullName = document.getElementById('editFullName').value;
    const email = document.getElementById('editEmail').value;
    const location = document.getElementById('editLocation').value;
    const desiredRole = document.getElementById('editDesiredRole').value;
    const bio = document.getElementById('editBio').value;
    const skills = document.getElementById('editSkills').value.split(',').map(skill => skill.trim());
    const experience = document.getElementById('editExperience').value;

    // Retrieve CSRF token from the meta tag
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    // Send POST request to update profile
    const response = await fetch('/profile', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-Token': csrfToken  // Ensure CSRF token is included
        },
        body: JSON.stringify({
            full_name: fullName,
            email: email,
            location: location,
            desired_role: desiredRole,
            bio: bio,
            skills: skills,
            experience: experience
        })
    });

    // Handle response
    if (response.ok) {
        alert('Profile updated successfully!');
        window.location.href = "{{ url_for('home') }}";
    } else {
        alert('Error updating profile. Please try again.');
    }
});
