import pytest
from pyplantuml import PlantUML

@pytest.fixture
def plantuml():
    return PlantUML()

def test_get_url(plantuml):
    plantuml_text = "@startuml\nactor Bob\n@enduml"
    url = plantuml.get_url(plantuml_text)
    assert url == "http://www.plantuml.com/plantuml/img/SoWkIImgAStDuGf9pKrBLWfIWhN8pKi1AStB0tKhEIbm58pKI5q0"

def test_processes(plantuml):
    plantuml_text = "@startuml\nactor Bob\n@enduml"
    image_data = plantuml.processes(plantuml_text)
    assert len(image_data) > 0

def test_processes_file(plantuml):
    filename = "test.puml"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("@startuml\nactor Bob\n@enduml")
    outfile = "test.png"
    errorfile = "test_error.html"
    plantuml.processes_file(filename, outfile=outfile, errorfile=errorfile)
    assert os.path.exists(outfile)
    assert os.path.exists(errorfile)

    # Clean up files after test is complete
    os.remove(filename)
    os.remove(outfile)
    os.remove(errorfile)