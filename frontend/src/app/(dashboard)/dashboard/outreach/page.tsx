import { Mail, Send } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

export default function OutreachPage() {
  return (
    <div className="mx-auto flex min-h-[100dvh] max-w-[1200px] flex-col gap-6 px-6 py-5">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div className="space-y-1">
          <h1 className="text-2xl font-semibold tracking-tight">Outreach</h1>
          <p className="text-sm text-muted-foreground">
            Draft and track follow-up emails to recruiters and hiring managers.
          </p>
        </div>
        <Button size="sm">
          <Send />
          Compose
        </Button>
      </header>

      <div className="grid min-h-[520px] gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.4fr)]">
        <Card className="flex flex-col border-border">
          <CardHeader className="border-b border-border pb-4">
            <CardTitle className="text-base">Messages</CardTitle>
            <CardDescription>Drafts and sent outreach.</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-1 flex-col items-center justify-center gap-2 py-16 text-center">
            <Mail className="size-7 text-muted-foreground" />
            <p className="text-sm font-medium">No messages yet</p>
            <p className="max-w-xs text-sm text-muted-foreground">
              Compose a follow-up email from a job or application to start
              outreach.
            </p>
          </CardContent>
        </Card>

        <Card className="flex flex-col border-border">
          <CardHeader className="border-b border-border pb-4">
            <CardTitle className="text-base">Preview</CardTitle>
            <CardDescription>
              Select a message to preview its content.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-1 flex-col items-center justify-center gap-2 py-16 text-center">
            <p className="text-sm text-muted-foreground">
              No message selected
            </p>
            <p className="max-w-sm text-xs text-muted-foreground">
              Your email subject, body, and recipient details will appear here.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
