import type { CV } from "@/lib/api/cvs"

export const cvs: CV[] = [
  {
    id: "cv_001",
    user_id: "usr_001",
    filename: "john_doe_cv.pdf",
    storage_key: "cvs/usr_001/john_doe_cv.pdf",
    is_active: true,
    created_at: "2026-06-01T10:00:00Z",
  },
  {
    id: "cv_002",
    user_id: "usr_001",
    filename: "john_doe_cv_v2.pdf",
    storage_key: "cvs/usr_001/john_doe_cv_v2.pdf",
    is_active: false,
    created_at: "2026-05-15T10:00:00Z",
  },
]