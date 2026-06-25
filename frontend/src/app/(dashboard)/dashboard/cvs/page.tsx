import { FileUp, Upload } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import type { CV } from "@/lib/api/cvs"

const cvs: CV[] = []

export default function CVsPage() {
  return (
    <div className="mx-auto flex max-w-[1200px] flex-col gap-6 px-6 py-5">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold tracking-tight">CVs</h1>
        <p className="text-sm text-muted-foreground">
          Upload resumes for parsing and semantic job matching.
        </p>
      </header>

      <Card className="border-border border-dashed">
        <CardContent className="flex flex-col items-center justify-center gap-4 px-6 py-16 text-center">
          <div className="flex size-12 items-center justify-center rounded-lg border border-border bg-[var(--color-accent-subtle)]">
            <Upload className="size-5 text-[var(--color-accent-hover)]" />
          </div>
          <div className="space-y-1">
            <p className="text-sm font-medium">Drop your CV here</p>
            <p className="max-w-sm text-sm text-muted-foreground">
              PDF or DOCX, up to 10 MB. Your file is stored securely and parsed
              for matching.
            </p>
          </div>
          <Button>
            <FileUp />
            Choose file
          </Button>
        </CardContent>
      </Card>

      <Card className="border-border">
        <CardHeader>
          <CardTitle className="text-base">Your CVs</CardTitle>
          <CardDescription>
            Select which resume to use for new searches.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {cvs.length === 0 ? (
            <div className="flex flex-col items-center justify-center gap-2 rounded-md border border-dashed border-border py-12 text-center">
              <p className="text-sm font-medium">No CVs uploaded</p>
              <p className="text-sm text-muted-foreground">
                Upload a resume to get started with job matching.
              </p>
            </div>
          ) : (
            <ul className="divide-y divide-border">
              {cvs.map((cv) => (
                <li
                  key={cv.id}
                  className="flex items-center justify-between py-3 text-sm"
                >
                  <span>{cv.original_filename}</span>
                  <span className="text-xs text-muted-foreground">
                    {cv.created_at}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
