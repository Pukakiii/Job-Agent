"use client"

import { useEffect, useRef, useState } from "react"
import { FileUp, Trash2, Upload } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { EmptyState } from "@/components/ui/empty-state"
import { ErrorBanner } from "@/components/ui/error-banner"
import { LoadingSkeleton } from "@/components/ui/loading-skeleton"
import { deleteCV, listCVs, uploadCV, type CV } from "@/lib/api/cvs"
import { toast } from "@/lib/toast"

export default function CVsPage() {
  const [cvs, setCvs] = useState<CV[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    let active = true

    async function load() {
      const result = await listCVs({ limit: 100 })
      if (!active) return

      if (!result.ok) {
        setError(result.error.message)
      } else {
        setCvs(result.data)
      }
      setLoading(false)
    }

    void load()

    return () => {
      active = false
    }
  }, [])

  async function handleUpload(file: File) {
    setUploading(true)
    setError(null)

    const result = await uploadCV(file)
    if (!result.ok) {
      setError(result.error.message)
      setUploading(false)
      return
    }

    toast.success("CV uploaded")
    const listResult = await listCVs({ limit: 100 })
    if (listResult.ok) {
      setCvs(listResult.data)
    }
    setUploading(false)
  }

  async function handleDelete(cvId: string) {
    const result = await deleteCV(cvId)
    if (!result.ok) {
      setError(result.error.message)
      return
    }

    setCvs((current) => current.filter((cv) => cv.id !== cvId))
    toast.success("CV deleted")
  }

  return (
    <div className="mx-auto flex max-w-[1200px] flex-col gap-6 px-4 py-5 sm:px-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold tracking-tight">CVs</h1>
        <p className="text-sm text-muted-foreground">
          Upload resumes for parsing and semantic job matching.
        </p>
      </header>

      {error ? (
        <ErrorBanner message={error} onDismiss={() => setError(null)} />
      ) : null}

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
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.doc,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            className="hidden"
            onChange={(event) => {
              const file = event.target.files?.[0]
              if (file) void handleUpload(file)
              event.target.value = ""
            }}
          />
          <Button
            disabled={uploading}
            onClick={() => fileInputRef.current?.click()}
          >
            <FileUp />
            {uploading ? "Uploading…" : "Choose file"}
          </Button>
        </CardContent>
      </Card>

      <Card className="border-border">
        <CardHeader>
          <CardTitle className="text-base">Your CVs</CardTitle>
          <CardDescription>
            The most recent upload is used for new searches.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <LoadingSkeleton rows={3} />
          ) : cvs.length === 0 ? (
            <EmptyState
              icon={Upload}
              title="No CVs uploaded"
              description="Upload a resume to get started with job matching."
            />
          ) : (
            <ul className="divide-y divide-border">
              {cvs.map((cv, index) => (
                <li
                  key={cv.id}
                  className="flex items-center justify-between gap-4 py-3 text-sm"
                >
                  <div className="min-w-0">
                    <p className="truncate font-medium">{cv.original_filename}</p>
                    <p className="text-xs text-muted-foreground">
                      {new Date(cv.created_at).toLocaleString()}
                      {index === 0 ? " · latest" : ""}
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon-sm"
                    aria-label={`Delete ${cv.original_filename}`}
                    onClick={() => void handleDelete(cv.id)}
                  >
                    <Trash2 className="size-4" />
                  </Button>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
