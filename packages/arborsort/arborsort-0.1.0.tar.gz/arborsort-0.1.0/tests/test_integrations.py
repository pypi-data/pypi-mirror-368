from arborsort.core import FileOrganizer

def test_organizer_integration(tmp_path):
    (tmp_path / "pic.png").write_text("image content")
    (tmp_path / "song.mp3").write_text("audio content")
    (tmp_path / "doc.pdf").write_text("document content")

    organizer = FileOrganizer(tmp_path)
    organizer.place_file_in_folder()

    assert (tmp_path / "Images" / "pic.png").exists()
    assert (tmp_path / "Audios" / "song.mp3").exists()
    assert (tmp_path / "Documents" / "doc.pdf").exists()
