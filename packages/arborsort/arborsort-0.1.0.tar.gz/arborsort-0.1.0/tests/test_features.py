from arborsort.core import organize_files_into_folders

def test_organize_files_into_folders(tmp_path):
    files = ["test.py","meet.txt","safe.png","prep.ppt","data.db","nothing.xcc"]
    for f in files:
        (tmp_path / f).write_text("This is a text file")
    organize_files_into_folders(tmp_path)

    assert (tmp_path / "Code" / "test.py").exists()     
    assert (tmp_path / "Documents" / "meet.txt").exists()        
    assert (tmp_path / "Images" / "safe.png").exists()        
    assert (tmp_path / "Presentations" / "prep.ppt").exists()        
    assert (tmp_path / "Database" / "data.db").exists()    
    assert (tmp_path / "Others" / "nothing.xcc").exists()    

    for f in files:
        assert not (tmp_path / f).exists()

