import os
import sys
from pathlib import Path

# Ensure the repository root is on sys.path so backend imports work.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from openai import OpenAI
import streamlit as st

from backend.memory_manager import load_project_memory as load_saved_memory, save_project_memory
from backend.project_manager import (
    create_project,
    create_user,
    load_code,
    save_code,
    load_wiring,
    load_chat_history,
    save_chat_history,
    load_learn_data,
)
from backend.prompt_builder import build_prompt
from backend.curriculum_manager import (
    available_levels,
    ensure_curriculum,
    load_level_devices,
    load_level_prompts,
)
from backend.user_manager import (
    ensure_user_db,
    verify_user,
    create_user_account,
    list_students,
    list_users,
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("PiPal")

st.subheader("Your AI Raspberry Pi Learning Companion")

repo_root = Path(__file__).resolve().parent.parent

# Ensure curriculum files are present so student onboarding can load device
# suggestions and project prompts for each learning level.
ensure_curriculum()

# Read the starter code from the shared project example so new workspaces
# can start from a known beginner-friendly example if explicitly requested.
with open(repo_root / "projects" / "blink_led.py", "r") as file:
    default_code = file.read()

users_root = repo_root / "users"
users_root.mkdir(parents=True, exist_ok=True)

if "selected_student" not in st.session_state:
    st.session_state.selected_student = None

if "selected_project" not in st.session_state:
    st.session_state.selected_project = None

if "user_level" not in st.session_state:
    st.session_state.user_level = "Beginner"

# Keep the default demo workspace for a first-time run so beginners have
# something to explore instantly, but do not pre-populate code in the UI.
if not any(users_root.iterdir()):
    create_user("student")
    create_project("student", "demo")

# Make sure the user database exists before allowing login.
ensure_user_db()

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

if "logged_in_role" not in st.session_state:
    st.session_state.logged_in_role = None

if not st.session_state.logged_in_user:
    st.header("PiPal Login")
    st.write("Please sign in with your username and password.")

    login_username = st.text_input("Username", key="login_username")
    login_password = st.text_input(
        "Password", type="password", key="login_password"
    )
    login_clicked = st.button("Login")

    if login_clicked:
        user = verify_user(login_username.strip(), login_password)
        if user:
            st.session_state.logged_in_user = login_username.strip()
            st.session_state.logged_in_role = user["role"]
            if user["role"] == "student":
                st.session_state.selected_student = login_username.strip()
                st.session_state.selected_project = None
                st.session_state.user_level = user.get("level", "Beginner")
            st.rerun()
        else:
            st.error("Invalid username or password.")

    st.stop()

logged_in_user = st.session_state.logged_in_user
logged_in_role = st.session_state.logged_in_role

st.sidebar.header("Workspace")
st.sidebar.caption("Use the sidebar to navigate PiPal.")

if logged_in_role == "admin":
    st.sidebar.subheader("Admin")
    st.sidebar.caption("Create student accounts and inspect classroom work.")

    new_student_name = st.sidebar.text_input(
        "New student username",
        key="admin_new_student_name",
    )
    new_student_password = st.sidebar.text_input(
        "New student password",
        type="password",
        key="admin_new_student_password",
    )
    new_student_level = st.sidebar.selectbox(
        "Student level",
        [level.title() for level in available_levels()],
        index=0,
        key="admin_new_student_level",
    )
    create_student_clicked = st.sidebar.button("Create Student")

    if create_student_clicked:
        cleaned_name = new_student_name.strip()
        cleaned_password = new_student_password.strip()
        cleaned_level = new_student_level.lower()
        if cleaned_name and cleaned_password:
            create_user_account(
                cleaned_name,
                cleaned_password,
                "student",
                cleaned_level,
            )
            create_user(cleaned_name)
            st.sidebar.success(
                f"Student account created for {cleaned_name} ({cleaned_level.title()})."
            )
        else:
            st.sidebar.warning("Enter both a student name and password.")

    st.sidebar.subheader("View Students")
    student_list = list_students()
    if student_list:
        for student_name in student_list:
            st.sidebar.write(f"• {student_name}")
    else:
        st.sidebar.write("No student accounts yet.")

    st.sidebar.subheader("Manage Templates")
    st.sidebar.caption("Create simple template files for projects.")
    template_name = st.sidebar.text_input(
        "New template name",
        key="admin_template_name",
    )
    create_template_clicked = st.sidebar.button("Create Template")
    templates_dir = repo_root / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)
    if create_template_clicked:
        cleaned_template = template_name.strip()
        if cleaned_template:
            (templates_dir / cleaned_template).write_text("# PiPal template\n")
            st.sidebar.success(f"Template created: {cleaned_template}")
        else:
            st.sidebar.warning("Enter a template name.")

    st.sidebar.caption("Available templates:")
    for template_file in sorted(templates_dir.iterdir()):
        st.sidebar.write(f"• {template_file.name}")

    st.sidebar.markdown("---")
    if st.sidebar.button("Logout", key="admin_logout"):
        st.session_state.logged_in_user = None
        st.session_state.logged_in_role = None
        st.rerun()

    st.sidebar.header("Inspect Student Projects")
    student_options = list_students()
    if not student_options:
        student_options = ["student"]
    selected_student = st.sidebar.selectbox(
        "Select student",
        student_options,
        key="selected_student",
    )

    selected_student_projects_dir = users_root / selected_student / "projects"
    selected_student_projects_dir.mkdir(parents=True, exist_ok=True)
    project_options = sorted(
        [path.name for path in selected_student_projects_dir.iterdir() if path.is_dir()]
    )
    if project_options:
        selected_project = st.sidebar.selectbox(
            "Select student project",
            project_options,
            key="selected_project",
        )
    else:
        selected_project = None
        st.sidebar.info("No projects exist for this student yet.")

    new_project_name = st.sidebar.text_input(
        "New project for student",
        key="admin_new_project_name",
    )
    create_project_clicked = st.sidebar.button("Create Project")

    if create_project_clicked:
        cleaned_project_name = new_project_name.strip()
        if cleaned_project_name:
            create_project(selected_student, cleaned_project_name)
            st.session_state.selected_project = cleaned_project_name
            st.sidebar.success(
                f"Project {cleaned_project_name} created for {selected_student}."
            )
            st.rerun()
        else:
            st.sidebar.warning("Enter a project name first.")
else:
    selected_student = st.session_state.logged_in_user
    student_level = st.session_state.user_level or "Beginner"
    st.sidebar.subheader("My Projects")
    st.sidebar.caption("Create and open your own project workspace.")

    selected_student_projects_dir = users_root / selected_student / "projects"
    selected_student_projects_dir.mkdir(parents=True, exist_ok=True)
    project_options = sorted(
        [path.name for path in selected_student_projects_dir.iterdir() if path.is_dir()]
    )

    new_project_name = st.sidebar.text_input(
        "New project name",
        key="student_new_project_name",
    )
    create_project_clicked = st.sidebar.button("Create Project")

    if create_project_clicked:
        cleaned_project_name = new_project_name.strip()
        if cleaned_project_name:
            create_project(selected_student, cleaned_project_name)
            st.session_state.selected_project = cleaned_project_name
            st.sidebar.success(f"Project {cleaned_project_name} created.")
            st.rerun()
        else:
            st.sidebar.warning("Enter a project name first.")

    if project_options:
        if (
            st.session_state.selected_project
            not in project_options
            or st.session_state.selected_project is None
        ):
            st.session_state.selected_project = project_options[0]

        selected_project = st.sidebar.selectbox(
            "Select project",
            project_options,
            key="selected_project",
        )
    else:
        selected_project = None
        st.sidebar.info("Create your first project to begin the guided workspace.")

    if st.sidebar.button("Logout", key="student_logout"):
        st.session_state.logged_in_user = None
        st.session_state.logged_in_role = None
        st.session_state.selected_project = None
        st.session_state.user_level = "Beginner"
        st.rerun()

if selected_student is None:
    st.error("No student workspace selected.")
    st.stop()

selected_student_projects_dir = users_root / selected_student / "projects"
selected_student_projects_dir.mkdir(parents=True, exist_ok=True)

if selected_project is None:
    if logged_in_role == "student":
        st.header("Welcome to your PiPal learning dashboard")
        st.caption(f"Level: {student_level}")

        devices = load_level_devices(student_level)
        prompts = load_level_prompts(student_level)

        st.subheader("Available devices")
        if devices:
            for device in devices:
                st.write(f"**{device.get('name', 'Device')}**: {device.get('description', '')}")
        else:
            st.write("No level devices found yet.")

        st.subheader("Suggested project ideas")
        if prompts:
            for suggestion in prompts:
                st.write(f"- {suggestion}")
        else:
            st.write("No project suggestions available yet.")

        st.info("Create a new project from the sidebar to begin the workspace.")
    else:
        st.header("Student project dashboard")
        st.write("Select or create a student project from the sidebar to inspect it.")
    st.stop()

project_dir = create_project(selected_student, selected_project)
project_code_path = project_dir / "code.py"
project_code = load_code(selected_student, selected_project, default_code="")
project_wiring = load_wiring(selected_student, selected_project)
project_learn = load_learn_data(selected_student, selected_project)
project_memory = load_saved_memory(selected_student, selected_project)
project_chat_history = load_chat_history(selected_student, selected_project)

project_dir = create_project(selected_student, selected_project)
project_code_path = project_dir / "code.py"
project_code = load_code(selected_student, selected_project, default_code)
project_wiring = load_wiring(selected_student, selected_project)
project_learn = load_learn_data(selected_student, selected_project)
project_memory = load_saved_memory(selected_student, selected_project)
project_chat_history = load_chat_history(selected_student, selected_project)

st.session_state.project_memory = project_memory

if (
    "active_project" not in st.session_state
    or st.session_state.active_project != (selected_student, selected_project)
):
    st.session_state.current_code = project_code
    st.session_state.chat_history = project_chat_history
    st.session_state.project_wiring = project_wiring
    st.session_state.project_learn = project_learn
    st.session_state.active_project = (selected_student, selected_project)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = project_chat_history

if "project_wiring" not in st.session_state:
    st.session_state.project_wiring = project_wiring

if "project_learn" not in st.session_state:
    st.session_state.project_learn = project_learn


def extract_modified_code(response_text: str):
    """Extract the updated code from the assistant response when it is included."""
    if "MODIFIED CODE:" not in response_text:
        return None

    code_block = response_text.split("MODIFIED CODE:", 1)[1]

    if "EXPLANATION:" in code_block:
        code_block = code_block.split("EXPLANATION:", 1)[0]

    code_block = code_block.strip()

    if code_block.startswith("```"):
        code_block = code_block.strip("`")
        if "\n" in code_block:
            code_block = code_block.split("\n", 1)[1]
        code_block = code_block.rsplit("```", 1)[0].strip()

    return code_block or None


def save_project_workspace(
    updated_code: str,
    user_request: str,
    username: str,
    project_name: str,
    project_dir: Path,
    project_code_path: Path,
    student_level: str,
):
    """Save updated code to the project workspace and update its learning memory."""
    backup_path = project_dir / "code_backup.py"

    if project_code_path.exists():
        backup_path.write_text(project_code_path.read_text())

    save_code(username, project_name, updated_code)

    project_memory = load_saved_memory(username, project_name)
    if not isinstance(project_memory.get("completed_steps"), list):
        project_memory["completed_steps"] = []

    project_memory["student_level"] = student_level
    project_memory["current_focus"] = "Code update"

    completed_step = f"Updated code for request: {user_request}"
    if completed_step not in project_memory["completed_steps"]:
        project_memory["completed_steps"].append(completed_step)

    save_project_memory(username, project_name, project_memory)
    return project_memory


st.header("Active Project")
st.caption(f"Workspace: {selected_student} / {selected_project}")

# Keep the main workspace focused on the active project and future-facing sections.
# The Code tab holds the editable project, while Wiring, Memory, and Learn are
# ready for future expansion without changing the current workflow.
tab_code, tab_wiring, tab_memory, tab_learn = st.tabs(
    ["Code", "Wiring", "Memory", "Learn"]
)

with tab_code:
    st.code(st.session_state.current_code, language="python")

with tab_wiring:
    st.write("Wiring assistance will be added here.")
    st.caption("Use this area for pin guidance and hardware help in future updates.")

with tab_memory:
    st.write("Project memory")
    st.json(st.session_state.project_memory)

with tab_learn:
    st.write("Learning guidance will appear here.")
    st.caption("This space can grow into guided prompts, checkpoints, and mini lessons.")

st.subheader("PiPal Chat")

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_message = st.chat_input("What would you like to change in the project?")

if user_message:
    prompt = (
        "Here is the current project code:\n"
        f"{st.session_state.current_code}\n\n"
        "Student request:\n"
        f"{user_message}\n\n"
        "Please update the code safely, keep it beginner friendly, add comments, "
        "and explain what changed simply."
    )

    st.session_state.chat_history.append({"role": "user", "content": user_message})
    save_chat_history(selected_student, selected_project, st.session_state.chat_history)

    if logged_in_role == "student":
        student_level = st.session_state.user_level or "Beginner"
    else:
        student_profile = list_users().get(selected_student, {})
        student_level = student_profile.get("level", "Beginner")

    messages = build_prompt(
        st.session_state.current_code,
        user_message,
        student_level,
        repo_root,
        project_memory=st.session_state.project_memory,
        username=selected_student,
        project_name=selected_project,
    )

    # Keep the chat history in the call so PiPal can remember the conversation.
    messages = [{"role": "system", "content": messages[0]["content"]}]
    messages.extend(st.session_state.chat_history)
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages
    )

    assistant_reply = response.choices[0].message.content
    updated_code = extract_modified_code(assistant_reply)

    if updated_code:
        st.session_state.current_code = updated_code
        st.session_state.project_memory = save_project_workspace(
            updated_code,
            user_message,
            selected_student,
            selected_project,
            project_dir,
            project_code_path,
            student_level,
        )

    st.session_state.chat_history.append(
        {"role": "assistant", "content": assistant_reply}
    )
    save_chat_history(selected_student, selected_project, st.session_state.chat_history)

    st.rerun()
