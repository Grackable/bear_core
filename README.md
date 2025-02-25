# BEAR - BE-A-Rigger | README (v1.0)

**Maya Rigging Tool**

BEAR claims to be the most intuitive and easy-to-use rigging tool available, offering production-proven features that streamline the rigging workflow for maximum efficiency and consistency.

Inspired by my time at Animal Logic Sydney, I started developing BEAR with the goal of creating a tool that is easy to use for everyone while providing a full range of advanced rigging features. While the codebase certainly has room for improvement, it was designed with a consistent structure to encourage user contributions, such as adding new rig components.

The UI design concept was developed at Arx Anima Vienna, followed by continous development on a freelance basis, which ultimately led to its utilization in the feature films *Die Heinzels 2 – Neue Mützen, neue Mission* and *Monstrous Mia*. From there, users and studios looking to improve production efficiency are invited to contribute to BEAR's development.

While the impact of rigging on the entire animation department is well recognized, the technical requirements it imposes on both the modeling department and character design are often undervalued by producers. BEAR aims to eliminate inefficient and complicated workflows, allowing artists to focus on asset rigging rather than bug fixing and scripted workarounds.

The BEAR UI is designed to be simple and accessible for new riggers while still offering all the features essential to professional rigging. As you explore its various utilities and additional UI snippets, you'll realize that BEAR provides much more than expected — covering nearly every production need and leaving little to be desired.

Be a part of it, BE-A-Rigger!

Visit the BEAR website for further information about its features:
https://www.bearigger.com/

**Installation Instructions**

1. Download the latest release package from github.
2. Create a folder named "bear" in your Maya user scripts folder.
3. Copy the installation files to the bear folder and run the following snippet in the Maya Script Editor:
from bear.ui import Builder
Builder.mainUI()
4. Optionally, create a shelf icon with the snippet and use this image:
bear/ui/icons/shelf_icon_builder.png