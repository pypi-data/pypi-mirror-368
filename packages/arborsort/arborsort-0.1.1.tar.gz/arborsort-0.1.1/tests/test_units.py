import pytest
from arborsort.core import FileOrganizer


def test_return_file(tmp_path):
    folder = tmp_path / "Test"
    folder.mkdir()
    file = folder / "test.txt"
    file.write_text("This is a test file")
    organizer = FileOrganizer(folder)
    assert "txt" == organizer.return_file_type(file)

def test_create_category(tmp_path):
    organizer = FileOrganizer(tmp_path)
    organizer.create_category_folder()
    
    expected_folders = ["Images", "Videos", "Documents", "Spreadsheets",
                        "Presentations", "Compressed", "Executable", "Code",
                        "Database", "Vector Graphics", "Audios",
                        "Fonts", "3D Models", "Disk Images", "Others"]
    for folder in expected_folders:
        (tmp_path / folder).exists()
    

def test_move_file(tmp_path):
    source = tmp_path / "test.txt"
    source.write_text("This is a test file")
    folder = tmp_path / "Test"
    folder.mkdir()
    organizer = FileOrganizer(folder)
    organizer.move_file(source,folder)
    assert not source.exists()
    assert (folder / "test.txt").exists()

@pytest.mark.parametrize("filename,expected_folder", [
    ("image.png", "Images"),
    ("video.mp4", "Videos"),
    ("audio.mp3", "Audios"),
    ("doc.pdf", "Documents"),
    ("sheet.xlsx", "Spreadsheets"),
    ("presentation.pptx", "Presentations"),
    ("archive.zip", "Compressed"),
    ("program.exe", "Executable"),
    ("script.py", "Code"),
    ("database.db", "Database"),
    ("design.ai", "Vector Graphics"),
    ("font.ttf", "Fonts"),
    ("model.obj", "3D Models"),
    ("disk.iso", "Disk Images"),
    ("unknown.xyz", "Others"),
])
def test_match_file_moves_to_correct_folder(tmp_path, filename, expected_folder):    
    file = tmp_path / filename
    file.write_text("This is a test file.")
    organizer = FileOrganizer(tmp_path)
    organizer.create_category_folder()
    organizer.match_file(file,tmp_path)

    assert not file.exists()
    assert (tmp_path / expected_folder / filename).exists()

def test_file_in_folder(tmp_path):
    files = ["test.py","meet.txt","safe.png","prep.ppt","data.db"]

    for file in files:
        (tmp_path / file).write_text("This is a test file")

    organizer = FileOrganizer(tmp_path)
    organizer.place_file_in_folder()   

    assert (tmp_path / "Code" / "test.py").exists()     
    assert (tmp_path / "Documents" / "meet.txt").exists()        
    assert (tmp_path / "Images" / "safe.png").exists()        
    assert (tmp_path / "Presentations" / "prep.ppt").exists()        
    assert (tmp_path / "Database" / "data.db").exists()