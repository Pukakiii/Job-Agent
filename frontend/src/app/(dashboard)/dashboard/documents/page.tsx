import { FileText, PenLine } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

export default function DocumentsPage() {
  return (
    <div className="mx-auto flex min-h-[100dvh] max-w-[1200px] flex-col gap-6 px-6 py-5">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold tracking-tight">Documents</h1>
        <p className="text-sm text-muted-foreground">
          AI-generated resumes and cover letters tailored to each role.
        </p>
      </header>

      <div className="grid gap-6 md:grid-cols-2">
        <Card className="border-border">
          <CardHeader>
            <div className="flex items-center gap-2">
              <FileText className="size-4 text-[var(--color-accent-hover)]" />
              <CardTitle className="text-base">Resumes</CardTitle>
            </div>
            <CardDescription>
              Tailored resume versions generated from your CV and job context.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col items-center justify-center gap-3 py-12 text-center">
            <p className="text-sm font-medium">No resumes generated</p>
            <p className="max-w-xs text-sm text-muted-foreground">
              Select a job and generate a tailored resume when you are ready to
              apply.
            </p>
            <Button variant="outline" size="sm">
              Generate resume
            </Button>
          </CardContent>
        </Card>

        <Card className="border-border">
          <CardHeader>
            <div className="flex items-center gap-2">
              <PenLine className="size-4 text-[var(--color-accent-hover)]" />
              <CardTitle className="text-base">Cover letters</CardTitle>
            </div>
            <CardDescription>
              Personalized cover letters aligned to each job description.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col items-center justify-center gap-3 py-12 text-center">
            <p className="text-sm font-medium">No cover letters yet</p>
            <p className="max-w-xs text-sm text-muted-foreground">
              Generate a cover letter from a saved job to speed up your
              applications.
            </p>
            <Button variant="outline" size="sm">
              Generate cover letter
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
