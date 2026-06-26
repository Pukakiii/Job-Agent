"use client"

import { useEffect, useState } from "react"
import { FileText, PenLine } from "lucide-react"

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
import {
  generateDocument,
  listDocuments,
  type DocumentType,
  type GeneratedDocument,
} from "@/lib/api/documents"
import { listJobs, type Job } from "@/lib/api/jobs"
import { toast } from "@/lib/toast"

export default function DocumentsPage() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [documents, setDocuments] = useState<GeneratedDocument[]>([])
  const [selectedJobId, setSelectedJobId] = useState("")
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState<DocumentType | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [preview, setPreview] = useState<GeneratedDocument | null>(null)

  useEffect(() => {
    let active = true

    async function load() {
      const [jobsRes, docsRes] = await Promise.all([
        listJobs({ limit: 100 }),
        listDocuments({ limit: 50 }),
      ])
      if (!active) return

      if (!jobsRes.ok) {
        setError(jobsRes.error.message)
      } else {
        setJobs(jobsRes.data)
        if (jobsRes.data[0]) setSelectedJobId(jobsRes.data[0].id)
      }

      if (docsRes.ok) {
        setDocuments(docsRes.data)
        if (docsRes.data[0]) setPreview(docsRes.data[0])
      }

      setLoading(false)
    }

    void load()
    return () => {
      active = false
    }
  }, [])

  async function handleGenerate(docType: DocumentType) {
    if (!selectedJobId) {
      toast.error("Select a job first")
      return
    }

    setGenerating(docType)
    setError(null)

    const result = await generateDocument({
      job_id: selectedJobId,
      doc_type: docType,
    })

    if (!result.ok) {
      setError(result.error.message)
      setGenerating(null)
      return
    }

    setDocuments((current) => [result.data, ...current])
    setPreview(result.data)
    toast.success(
      docType === "resume" ? "Resume generated" : "Cover letter generated",
    )
    setGenerating(null)
  }

  const resumes = documents.filter((doc) => doc.doc_type === "resume")
  const coverLetters = documents.filter((doc) => doc.doc_type === "cover_letter")

  return (
    <div className="mx-auto flex max-w-[1200px] flex-col gap-6 px-4 py-5 sm:px-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold tracking-tight">Documents</h1>
        <p className="text-sm text-muted-foreground">
          AI-generated resumes and cover letters tailored to each role.
        </p>
      </header>

      {error ? (
        <ErrorBanner message={error} onDismiss={() => setError(null)} />
      ) : null}

      <Card className="border-border">
        <CardHeader>
          <CardTitle className="text-base">Target job</CardTitle>
          <CardDescription>
            Pick a job before generating tailored documents.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-3 sm:flex-row sm:items-end">
          {loading ? (
            <LoadingSkeleton rows={1} />
          ) : jobs.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No jobs in corpus yet — run a search first.
            </p>
          ) : (
            <div className="flex flex-1 flex-col gap-2">
              <label htmlFor="job-picker" className="text-sm font-medium">
                Job
              </label>
              <select
                id="job-picker"
                className="h-9 rounded-md border border-border bg-background px-3 text-sm"
                value={selectedJobId}
                onChange={(event) => setSelectedJobId(event.target.value)}
              >
                {jobs.map((job) => (
                  <option key={job.id} value={job.id}>
                    {job.title}
                    {job.company ? ` · ${job.company}` : ""}
                  </option>
                ))}
              </select>
            </div>
          )}
        </CardContent>
      </Card>

      <div className="grid gap-6 md:grid-cols-2">
        <Card className="border-border">
          <CardHeader>
            <div className="flex items-center gap-2">
              <FileText className="size-4 text-[var(--color-accent-hover)]" />
              <CardTitle className="text-base">Resumes</CardTitle>
            </div>
            <CardDescription>
              Tailored resume versions ({resumes.length} generated).
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-3">
            <Button
              variant="outline"
              size="sm"
              disabled={!selectedJobId || generating !== null}
              onClick={() => void handleGenerate("resume")}
            >
              {generating === "resume" ? "Generating…" : "Generate resume"}
            </Button>
            {resumes.length === 0 ? (
              <EmptyState
                icon={FileText}
                title="No resumes generated"
                description="Select a job and generate a tailored resume."
              />
            ) : (
              <ul className="space-y-2 text-sm">
                {resumes.map((doc) => (
                  <li key={doc.id}>
                    <button
                      type="button"
                      className="text-left text-primary underline-offset-4 hover:underline"
                      onClick={() => setPreview(doc)}
                    >
                      Resume · {new Date(doc.created_at).toLocaleString()}
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        <Card className="border-border">
          <CardHeader>
            <div className="flex items-center gap-2">
              <PenLine className="size-4 text-[var(--color-accent-hover)]" />
              <CardTitle className="text-base">Cover letters</CardTitle>
            </div>
            <CardDescription>
              Role-specific letters ({coverLetters.length} generated).
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-3">
            <Button
              variant="outline"
              size="sm"
              disabled={!selectedJobId || generating !== null}
              onClick={() => void handleGenerate("cover_letter")}
            >
              {generating === "cover_letter"
                ? "Generating…"
                : "Generate cover letter"}
            </Button>
            {coverLetters.length === 0 ? (
              <EmptyState
                icon={PenLine}
                title="No cover letters generated"
                description="Select a job and generate a tailored cover letter."
              />
            ) : (
              <ul className="space-y-2 text-sm">
                {coverLetters.map((doc) => (
                  <li key={doc.id}>
                    <button
                      type="button"
                      className="text-left text-primary underline-offset-4 hover:underline"
                      onClick={() => setPreview(doc)}
                    >
                      Cover letter · {new Date(doc.created_at).toLocaleString()}
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </div>

      {preview ? (
        <Card className="border-border">
          <CardHeader>
            <CardTitle className="text-base">Preview</CardTitle>
            <CardDescription>
              {preview.doc_type === "resume" ? "Resume" : "Cover letter"} ·{" "}
              {new Date(preview.created_at).toLocaleString()}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <pre className="max-h-[480px] overflow-auto whitespace-pre-wrap rounded-md border border-border bg-muted/30 p-4 text-sm">
              {preview.content}
            </pre>
          </CardContent>
        </Card>
      ) : null}
    </div>
  )
}
