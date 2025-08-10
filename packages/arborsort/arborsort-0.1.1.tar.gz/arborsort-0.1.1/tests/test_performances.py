from arborsort.core import FileOrganizer

def test_place_file_performance(benchmark, tmp_path):
    for i in range(1000):
        (tmp_path / f"file{i}.txt").write_text("data")

    organizer = FileOrganizer(tmp_path)
    
    benchmark(organizer.place_file_in_folder)
