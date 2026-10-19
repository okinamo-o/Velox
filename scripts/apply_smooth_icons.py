#!/usr/bin/env python3
"""
Applies Velox Smooth Rounded & Aerodynamic vector icons across Chrome and Components.
"""

import os
from validate_icons import validate_icon_content

SRC = r"D:\Velox\src"

ICONS = {
    # 1. Back Arrow
    os.path.join(SRC, "components", "vector_icons", "back_arrow_chrome_refresh.icon"): """// Copyright 2024 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

CANVAS_DIMENSIONS, 20,
FILL_RULE_NONZERO,
MOVE_TO, 7.82f, 10.75f,
LINE_TO, 11.41f, 14.34f,
ARC_TO, 1.06f, 1.06f, 0, 0, 1, 9.91f, 15.84f,
LINE_TO, 4.86f, 10.79f,
ARC_TO, 1.12f, 1.12f, 0, 0, 1, 4.86f, 9.21f,
LINE_TO, 9.91f, 4.16f,
ARC_TO, 1.06f, 1.06f, 0, 1, 1, 11.41f, 5.66f,
LINE_TO, 7.82f, 9.25f,
H_LINE_TO, 15.25f,
ARC_TO, 0.75f, 0.75f, 0, 0, 1, 16.0f, 10.0f,
ARC_TO, 0.75f, 0.75f, 0, 0, 1, 15.25f, 10.75f,
CLOSE
""",

    # 2. Forward Arrow
    os.path.join(SRC, "components", "vector_icons", "forward_arrow_chrome_refresh.icon"): """// Copyright 2024 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

CANVAS_DIMENSIONS, 20,
FILL_RULE_NONZERO,
MOVE_TO, 12.18f, 9.25f,
LINE_TO, 8.59f, 5.66f,
ARC_TO, 1.06f, 1.06f, 0, 0, 1, 10.09f, 4.16f,
LINE_TO, 15.14f, 9.21f,
ARC_TO, 1.12f, 1.12f, 0, 0, 1, 15.14f, 10.79f,
LINE_TO, 10.09f, 15.84f,
ARC_TO, 1.06f, 1.06f, 0, 1, 1, 8.59f, 14.34f,
LINE_TO, 12.18f, 10.75f,
H_LINE_TO, 4.75f,
ARC_TO, 0.75f, 0.75f, 0, 0, 1, 4.0f, 10.0f,
ARC_TO, 0.75f, 0.75f, 0, 0, 1, 4.75f, 9.25f,
CLOSE
""",

    # 3. Reload Button
    os.path.join(SRC, "components", "vector_icons", "reload_chrome_refresh.icon"): """// Copyright 2024 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

CANVAS_DIMENSIONS, 20,
FILL_RULE_NONZERO,
MOVE_TO, 10, 16,
ARC_TO, 6, 6, 0, 1, 1, 15.65f, 7.85f,
LINE_TO, 16.2f, 5.7f,
ARC_TO, 0.6f, 0.6f, 0, 0, 1, 17.2f, 5.4f,
LINE_TO, 17.3f, 9.3f,
ARC_TO, 0.7f, 0.7f, 0, 0, 1, 16.6f, 10.0f,
LINE_TO, 12.7f, 9.9f,
ARC_TO, 0.6f, 0.6f, 0, 0, 1, 12.4f, 8.9f,
LINE_TO, 14.4f, 8.4f,
ARC_TO, 4.6f, 4.6f, 0, 1, 0, 10, 14.6f,
ARC_TO, 4.6f, 4.6f, 0, 0, 0, 13.9f, 12.4f,
ARC_TO, 0.7f, 0.7f, 0, 1, 1, 15.1f, 13.1f,
ARC_TO, 6, 6, 0, 0, 1, 10, 16,
CLOSE
""",

    # 4. App Menu (3 Dots)
    os.path.join(SRC, "chrome", "app", "vector_icons", "browser_tools_chrome_refresh.icon"): """// Copyright 2023 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

CANVAS_DIMENSIONS, 20,
CIRCLE, 10, 4.5f, 1.6f,
CIRCLE, 10, 10.0f, 1.6f,
CIRCLE, 10, 15.5f, 1.6f
""",

    # 5. Passwords & Autofill (Key)
    os.path.join(SRC, "components", "vector_icons", "password_manager.icon"): """// Copyright 2024 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

CANVAS_DIMENSIONS, 20,
FILL_RULE_NONZERO,
MOVE_TO, 6.5f, 14.0f,
ARC_TO, 4.0f, 4.0f, 0, 1, 1, 10.2f, 8.5f,
H_LINE_TO, 16.5f,
ARC_TO, 0.75f, 0.75f, 0, 0, 1, 17.25f, 9.25f,
V_LINE_TO, 12.0f,
ARC_TO, 0.75f, 0.75f, 0, 0, 1, 16.5f, 12.75f,
H_LINE_TO, 15.0f,
V_LINE_TO, 11.25f,
H_LINE_TO, 13.5f,
V_LINE_TO, 13.0f,
ARC_TO, 0.75f, 0.75f, 0, 0, 1, 12.75f, 13.75f,
H_LINE_TO, 11.5f,
ARC_TO, 0.75f, 0.75f, 0, 0, 1, 10.75f, 13.0f,
V_LINE_TO, 11.0f,
H_LINE_TO, 9.8f,
ARC_TO, 4.0f, 4.0f, 0, 0, 1, 6.5f, 14.0f,
CLOSE,
MOVE_TO, 6.5f, 11.5f,
ARC_TO, 1.5f, 1.5f, 0, 1, 0, 5.0f, 10.0f,
ARC_TO, 1.5f, 1.5f, 0, 0, 0, 6.5f, 11.5f,
CLOSE
""",

    # 6. Customize Profile (Pencil / Stylus)
    os.path.join(SRC, "components", "vector_icons", "edit_chrome_refresh.icon"): """// Copyright 2024 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

CANVAS_DIMENSIONS, 20,
FILL_RULE_NONZERO,
MOVE_TO, 14.85f, 3.65f,
ARC_TO, 1.6f, 1.6f, 0, 0, 1, 17.1f, 5.9f,
LINE_TO, 7.8f, 15.2f,
ARC_TO, 0.8f, 0.8f, 0, 0, 1, 7.2f, 15.45f,
LINE_TO, 4.3f, 16.0f,
ARC_TO, 0.5f, 0.5f, 0, 0, 1, 3.8f, 15.5f,
LINE_TO, 4.35f, 12.6f,
ARC_TO, 0.8f, 0.8f, 0, 0, 1, 4.6f, 12.0f,
CLOSE,
MOVE_TO, 13.75f, 4.75f,
LINE_TO, 6.0f, 12.5f,
LINE_TO, 5.65f, 14.15f,
LINE_TO, 7.3f, 13.8f,
LINE_TO, 15.05f, 6.05f,
CLOSE
""",

    # 7. Profile Avatar Toolbar Button
    os.path.join(SRC, "chrome", "app", "vector_icons", "user_account_avatar_refresh.icon"): """// Copyright 2023 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

CANVAS_DIMENSIONS, 20,
FILL_RULE_NONZERO,
CIRCLE, 10, 7.5f, 2.75f,
MOVE_TO, 4.5f, 16.5f,
ARC_TO, 5.5f, 5.5f, 0, 0, 1, 10.0f, 12.0f,
ARC_TO, 5.5f, 5.5f, 0, 0, 1, 15.5f, 16.5f,
ARC_TO, 0.75f, 0.75f, 0, 0, 1, 14.75f, 17.25f,
H_LINE_TO, 5.25f,
ARC_TO, 0.75f, 0.75f, 0, 0, 1, 4.5f, 16.5f,
CLOSE,
MOVE_TO, 10, 19,
ARC_TO, 9, 9, 0, 1, 1, 19, 10,
ARC_TO, 9, 9, 0, 0, 1, 10, 19,
CLOSE,
MOVE_TO, 10, 17.5f,
ARC_TO, 7.5f, 7.5f, 0, 1, 0, 2.5f, 10,
ARC_TO, 7.5f, 7.5f, 0, 0, 0, 10, 17.5f,
CLOSE
""",

    # 8. Profile Circle Header Icon
    os.path.join(SRC, "chrome", "app", "vector_icons", "account_circle_chrome_refresh.icon"): """// Copyright 2023 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

CANVAS_DIMENSIONS, 20,
FILL_RULE_NONZERO,
CIRCLE, 10, 7.5f, 2.75f,
MOVE_TO, 4.5f, 16.5f,
ARC_TO, 5.5f, 5.5f, 0, 0, 1, 10.0f, 12.0f,
ARC_TO, 5.5f, 5.5f, 0, 0, 1, 15.5f, 16.5f,
ARC_TO, 0.75f, 0.75f, 0, 0, 1, 14.75f, 17.25f,
H_LINE_TO, 5.25f,
ARC_TO, 0.75f, 0.75f, 0, 0, 1, 4.5f, 16.5f,
CLOSE,
MOVE_TO, 10, 19,
ARC_TO, 9, 9, 0, 1, 1, 19, 10,
ARC_TO, 9, 9, 0, 0, 1, 10, 19,
CLOSE,
MOVE_TO, 10, 17.5f,
ARC_TO, 7.5f, 7.5f, 0, 1, 0, 2.5f, 10,
ARC_TO, 7.5f, 7.5f, 0, 0, 0, 10, 17.5f,
CLOSE
""",

    # 9. Add Profile (Account +)
    os.path.join(SRC, "chrome", "app", "vector_icons", "account_add_chrome_refresh.icon"): """// Copyright 2024 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

CANVAS_DIMENSIONS, 16,
FILL_RULE_NONZERO,
CIRCLE, 5.5f, 5.0f, 2.2f,
MOVE_TO, 1.5f, 13.0f,
ARC_TO, 4.0f, 4.0f, 0, 0, 1, 5.5f, 9.0f,
ARC_TO, 4.0f, 4.0f, 0, 0, 1, 9.5f, 13.0f,
ARC_TO, 0.6f, 0.6f, 0, 0, 1, 8.9f, 13.6f,
H_LINE_TO, 2.1f,
ARC_TO, 0.6f, 0.6f, 0, 0, 1, 1.5f, 13.0f,
CLOSE,
MOVE_TO, 13.0f, 4.0f,
ARC_TO, 0.6f, 0.6f, 0, 0, 1, 13.6f, 4.6f,
V_LINE_TO, 6.4f,
H_LINE_TO, 15.4f,
ARC_TO, 0.6f, 0.6f, 0, 0, 1, 16.0f, 7.0f,
ARC_TO, 0.6f, 0.6f, 0, 0, 1, 15.4f, 7.6f,
H_LINE_TO, 13.6f,
V_LINE_TO, 9.4f,
ARC_TO, 0.6f, 0.6f, 0, 0, 1, 13.0f, 10.0f,
ARC_TO, 0.6f, 0.6f, 0, 0, 1, 12.4f, 9.4f,
V_LINE_TO, 7.6f,
H_LINE_TO, 10.6f,
ARC_TO, 0.6f, 0.6f, 0, 0, 1, 10.0f, 7.0f,
ARC_TO, 0.6f, 0.6f, 0, 0, 1, 10.6f, 6.4f,
H_LINE_TO, 12.4f,
V_LINE_TO, 4.6f,
ARC_TO, 0.6f, 0.6f, 0, 0, 1, 13.0f, 4.0f,
CLOSE
""",

    # 10. Open Guest Profile (Squircle Card)
    os.path.join(SRC, "chrome", "app", "vector_icons", "account_box.icon"): """// Copyright 2024 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

CANVAS_DIMENSIONS, 960,
FILL_RULE_NONZERO,
ROUND_RECT, 120, 120, 720, 720, 160,
MOVE_TO, 480, 260,
ARC_TO, 120, 120, 0, 1, 0, 480, 500,
ARC_TO, 120, 120, 0, 0, 0, 480, 260,
CLOSE,
MOVE_TO, 240, 740,
ARC_TO, 240, 240, 0, 0, 1, 480, 540,
ARC_TO, 240, 240, 0, 0, 1, 720, 740,
CLOSE
""",

    # 11. Manage Profiles (Two Accounts / Layered)
    os.path.join(SRC, "chrome", "app", "vector_icons", "account_manage_chrome_refresh.icon"): """// Copyright 2024 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

CANVAS_DIMENSIONS, 16,
FILL_RULE_NONZERO,
CIRCLE, 5.5f, 4.5f, 2.0f,
MOVE_TO, 1.5f, 13.0f,
ARC_TO, 4.0f, 4.0f, 0, 0, 1, 5.5f, 9.0f,
ARC_TO, 4.0f, 4.0f, 0, 0, 1, 9.5f, 13.0f,
ARC_TO, 0.6f, 0.6f, 0, 0, 1, 8.9f, 13.6f,
H_LINE_TO, 2.1f,
ARC_TO, 0.6f, 0.6f, 0, 0, 1, 1.5f, 13.0f,
CLOSE,
CIRCLE, 11.5f, 5.5f, 1.8f,
MOVE_TO, 9.5f, 12.0f,
ARC_TO, 3.5f, 3.5f, 0, 0, 1, 11.5f, 9.5f,
ARC_TO, 3.5f, 3.5f, 0, 0, 1, 15.0f, 13.0f,
ARC_TO, 0.6f, 0.6f, 0, 0, 1, 14.4f, 13.6f,
H_LINE_TO, 10.2f,
LINE_TO, 9.5f, 12.0f,
CLOSE
""",

    # 12. Bookmark Star (Active / Filled)
    os.path.join(SRC, "components", "omnibox", "browser", "vector_icons", "star_active_chrome_refresh.icon"): """// Copyright 2023 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

CANVAS_DIMENSIONS, 20,
FILL_RULE_NONZERO,
MOVE_TO, 9.38f, 2.87f,
ARC_TO, 0.7f, 0.7f, 0, 0, 1, 10.62f, 2.87f,
LINE_TO, 12.5f, 7.42f,
ARC_TO, 0.7f, 0.7f, 0, 0, 0, 13.08f, 7.84f,
LINE_TO, 18.0f, 8.28f,
ARC_TO, 0.7f, 0.7f, 0, 0, 1, 18.4f, 9.49f,
LINE_TO, 14.65f, 12.78f,
ARC_TO, 0.7f, 0.7f, 0, 0, 0, 14.45f, 13.41f,
LINE_TO, 15.57f, 18.23f,
ARC_TO, 0.7f, 0.7f, 0, 0, 1, 14.53f, 18.99f,
LINE_TO, 10.35f, 16.42f,
ARC_TO, 0.7f, 0.7f, 0, 0, 0, 9.65f, 16.42f,
LINE_TO, 5.47f, 18.99f,
ARC_TO, 0.7f, 0.7f, 0, 0, 1, 4.43f, 18.23f,
LINE_TO, 5.55f, 13.41f,
ARC_TO, 0.7f, 0.7f, 0, 0, 0, 5.35f, 12.78f,
LINE_TO, 1.6f, 9.49f,
ARC_TO, 0.7f, 0.7f, 0, 0, 1, 2.0f, 8.28f,
LINE_TO, 6.92f, 7.84f,
ARC_TO, 0.7f, 0.7f, 0, 0, 0, 7.5f, 7.42f,
CLOSE
""",

    # 13. Bookmark Star (Outline)
    os.path.join(SRC, "components", "omnibox", "browser", "vector_icons", "star_chrome_refresh.icon"): """// Copyright 2023 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

CANVAS_DIMENSIONS, 20,
FILL_RULE_NONZERO,
MOVE_TO, 9.38f, 2.87f,
ARC_TO, 0.7f, 0.7f, 0, 0, 1, 10.62f, 2.87f,
LINE_TO, 12.5f, 7.42f,
ARC_TO, 0.7f, 0.7f, 0, 0, 0, 13.08f, 7.84f,
LINE_TO, 18.0f, 8.28f,
ARC_TO, 0.7f, 0.7f, 0, 0, 1, 18.4f, 9.49f,
LINE_TO, 14.65f, 12.78f,
ARC_TO, 0.7f, 0.7f, 0, 0, 0, 14.45f, 13.41f,
LINE_TO, 15.57f, 18.23f,
ARC_TO, 0.7f, 0.7f, 0, 0, 1, 14.53f, 18.99f,
LINE_TO, 10.35f, 16.42f,
ARC_TO, 0.7f, 0.7f, 0, 0, 0, 9.65f, 16.42f,
LINE_TO, 5.47f, 18.99f,
ARC_TO, 0.7f, 0.7f, 0, 0, 1, 4.43f, 18.23f,
LINE_TO, 5.55f, 13.41f,
ARC_TO, 0.7f, 0.7f, 0, 0, 0, 5.35f, 12.78f,
LINE_TO, 1.6f, 9.49f,
ARC_TO, 0.7f, 0.7f, 0, 0, 1, 2.0f, 8.28f,
LINE_TO, 6.92f, 7.84f,
ARC_TO, 0.7f, 0.7f, 0, 0, 0, 7.5f, 7.42f,
CLOSE,
MOVE_TO, 10.0f, 5.2f,
LINE_TO, 8.35f, 8.95f,
LINE_TO, 4.35f, 9.35f,
LINE_TO, 7.4f, 12.0f,
LINE_TO, 6.5f, 16.0f,
LINE_TO, 10.0f, 13.9f,
LINE_TO, 13.5f, 16.0f,
LINE_TO, 12.6f, 12.0f,
LINE_TO, 15.65f, 9.35f,
LINE_TO, 11.65f, 8.95f,
CLOSE
""",

    # 14. Side Panel
    os.path.join(SRC, "chrome", "app", "vector_icons", "side_panel.icon"): """// Copyright 2021 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

CANVAS_DIMENSIONS, 16,
FLIPS_IN_RTL,
FILL_RULE_NONZERO,
MOVE_TO, 13.5f, 1.5f,
H_LINE_TO, 2.5f,
ARC_TO, 1.5f, 1.5f, 0, 0, 0, 1.0f, 3.0f,
V_LINE_TO, 13.0f,
ARC_TO, 1.5f, 1.5f, 0, 0, 0, 2.5f, 14.5f,
H_LINE_TO, 13.5f,
ARC_TO, 1.5f, 1.5f, 0, 0, 0, 15.0f, 13.0f,
V_LINE_TO, 3.0f,
ARC_TO, 1.5f, 1.5f, 0, 0, 0, 13.5f, 1.5f,
CLOSE,
MOVE_TO, 9.75f, 3.0f,
H_LINE_TO, 3.0f,
ARC_TO, 0.75f, 0.75f, 0, 0, 0, 2.25f, 3.75f,
V_LINE_TO, 12.25f,
ARC_TO, 0.75f, 0.75f, 0, 0, 0, 3.0f, 13.0f,
H_LINE_TO, 9.75f,
V_LINE_TO, 3.0f,
CLOSE
""",

    # 15. Media Toolbar Controls
    os.path.join(SRC, "chrome", "app", "vector_icons", "media_toolbar_button_chrome_refresh.icon"): """// Copyright 2024 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

CANVAS_DIMENSIONS, 20,
FILL_RULE_NONZERO,
CIRCLE, 13.0f, 12.5f, 2.5f,
MOVE_TO, 14.5f, 12.5f,
V_LINE_TO, 4.75f,
ARC_TO, 0.75f, 0.75f, 0, 0, 1, 15.25f, 4.0f,
H_LINE_TO, 17.25f,
ARC_TO, 0.75f, 0.75f, 0, 0, 1, 18.0f, 4.75f,
ARC_TO, 0.75f, 0.75f, 0, 0, 1, 17.25f, 5.5f,
H_LINE_TO, 15.5f,
V_LINE_TO, 12.5f,
CLOSE,
ROUND_RECT, 2.5f, 4.25f, 8.0f, 1.5f, 0.75f,
ROUND_RECT, 2.5f, 7.25f, 8.0f, 1.5f, 0.75f,
ROUND_RECT, 2.5f, 10.25f, 5.5f, 1.5f, 0.75f
""",
}

def main():
    errors = 0
    for path, content in ICONS.items():
        ok, msg = validate_icon_content(content)
        if not ok:
            print(f"Error validating {os.path.basename(path)}: {msg}")
            errors += 1
            continue
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated: {os.path.basename(path)}")
    if errors == 0:
        print("\nAll icons successfully updated and validated!")
    else:
        print(f"\nCompleted with {errors} errors.")

if __name__ == "__main__":
    main()
