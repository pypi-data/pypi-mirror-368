from pathlib import Path
import shutil

root = Path(__file__)
input_folder = root.parents[1] / 'translation/bin/x64/Debug'
output_folder = root.parent / 'pbi_prototype_query_translation/libs'
output_folder.mkdir(parents=True, exist_ok=True)
# (output_folder / '__init__.py').write_text("# Just here to remind hatchling that we want this too")

for f in output_folder.iterdir():
    f.unlink()

for f in input_folder.iterdir():
    if f.is_dir():
        continue
    if f.name in (
        'Microsoft.PowerBI.ClientResources.dll', 
        'Microsoft.Mashup.Client.Desktop.UI.dll',
        'Microsoft.PowerBI.Client.Windows.Themes.dll',
        'msmdrsv.exe'
    ):
        continue
    shutil.copy(
        f.absolute().as_posix(),
        (output_folder / f.name).absolute().as_posix()  
    )