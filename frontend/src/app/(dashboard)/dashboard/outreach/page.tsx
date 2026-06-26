"use client"

import { useEffect, useState } from "react"
import { Mail, Send } from "lucide-react"

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
import { Input } from "@/components/ui/input"
import { LoadingSkeleton } from "@/components/ui/loading-skeleton"
import {
  listOutreach,
  sendOutreach,
  type OutreachEmail,
} from "@/lib/api/outreach"
import { toast } from "@/lib/toast"

export default function OutreachPage() {
  const [messages, setMessages] = useState<OutreachEmail[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [toAddress, setToAddress] = useState("")
  const [subject, setSubject] = useState("")
  const [body, setBody] = useState("")

  const selected = messages.find((message) => message.id === selectedId) ?? null

  useEffect(() => {
    let active = true

    async function load() {
      const result = await listOutreach({ limit: 50 })
      if (!active) return

      if (!result.ok) {
        setError(result.error.message)
      } else {
        setMessages(result.data)
        if (result.data[0]) setSelectedId(result.data[0].id)
      }
      setLoading(false)
    }

    void load()
    return () => {
      active = false
    }
  }, [])

  async function handleSend() {
    if (!toAddress.trim() || !subject.trim() || !body.trim()) {
      toast.error("Fill in recipient, subject, and body")
      return
    }

    setSending(true)
    setError(null)

    const result = await sendOutreach({
      to_address: toAddress.trim(),
      subject: subject.trim(),
      body: body.trim(),
    })

    if (!result.ok) {
      setError(result.error.message)
      setSending(false)
      return
    }

    setMessages((current) => [result.data, ...current])
    setSelectedId(result.data.id)
    setToAddress("")
    setSubject("")
    setBody("")
    toast.success("Outreach email sent (or stubbed without Postmark token)")
    setSending(false)
  }

  return (
    <div className="mx-auto flex max-w-[1200px] flex-col gap-6 px-4 py-5 sm:px-6">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div className="space-y-1">
          <h1 className="text-2xl font-semibold tracking-tight">Outreach</h1>
          <p className="text-sm text-muted-foreground">
            Draft and track follow-up emails to recruiters and hiring managers.
          </p>
        </div>
      </header>

      {error ? (
        <ErrorBanner message={error} onDismiss={() => setError(null)} />
      ) : null}

      <div className="grid min-h-[520px] gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.4fr)]">
        <Card className="flex flex-col border-border">
          <CardHeader className="border-b border-border pb-4">
            <CardTitle className="text-base">Messages</CardTitle>
            <CardDescription>Drafts and sent outreach.</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-1 flex-col gap-2 py-4">
            {loading ? (
              <LoadingSkeleton rows={4} />
            ) : messages.length === 0 ? (
              <EmptyState
                icon={Mail}
                title="No messages yet"
                description="Compose a follow-up email to start outreach."
              />
            ) : (
              <ul className="space-y-2">
                {messages.map((message) => (
                  <li key={message.id}>
                    <button
                      type="button"
                      onClick={() => setSelectedId(message.id)}
                      className={`w-full rounded-md border px-3 py-2 text-left text-sm ${
                        selectedId === message.id
                          ? "border-primary bg-muted/50"
                          : "border-border"
                      }`}
                    >
                      <p className="font-medium">{message.subject}</p>
                      <p className="text-xs text-muted-foreground">
                        {message.to_address} · {message.status}
                      </p>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        <Card className="flex flex-col border-border">
          <CardHeader className="border-b border-border pb-4">
            <CardTitle className="text-base">Compose</CardTitle>
            <CardDescription>
              Send outreach via Postmark when configured, otherwise stubbed.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-1 flex-col gap-4 py-4">
            <div className="space-y-2">
              <label htmlFor="to" className="text-sm font-medium">
                Recipient
              </label>
              <Input
                id="to"
                type="email"
                placeholder="recruiter@company.com"
                value={toAddress}
                onChange={(event) => setToAddress(event.target.value)}
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="subject" className="text-sm font-medium">
                Subject
              </label>
              <Input
                id="subject"
                value={subject}
                onChange={(event) => setSubject(event.target.value)}
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="body" className="text-sm font-medium">
                Body
              </label>
              <textarea
                id="body"
                rows={8}
                value={body}
                onChange={(event) => setBody(event.target.value)}
                className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
              />
            </div>
            <Button size="sm" disabled={sending} onClick={() => void handleSend()}>
              <Send />
              {sending ? "Sending…" : "Send"}
            </Button>

            {selected ? (
              <div className="mt-4 rounded-md border border-border bg-muted/20 p-4 text-sm">
                <p className="mb-2 font-medium">Selected preview</p>
                <p className="text-xs text-muted-foreground">
                  To: {selected.to_address}
                </p>
                <pre className="mt-2 max-h-48 overflow-auto whitespace-pre-wrap">
                  {selected.body}
                </pre>
              </div>
            ) : null}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
