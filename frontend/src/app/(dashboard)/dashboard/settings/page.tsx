import { AlertTriangle } from "lucide-react"

import { ThemeAppearanceSettings } from "@/components/theme/theme-appearance-settings"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Separator } from "@/components/ui/separator"

export default function SettingsPage() {
  return (
    <div className="mx-auto flex max-w-[1200px] flex-col gap-6 px-6 py-5">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold tracking-tight">Settings</h1>
        <p className="text-sm text-muted-foreground">
          Manage your account and AI matching preferences.
        </p>
      </header>

      <Card className="border-border">
        <CardHeader>
          <CardTitle className="text-base">Account</CardTitle>
          <CardDescription>
            Your profile and sign-in details.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium">
                Email
              </label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                disabled
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="name" className="text-sm font-medium">
                Display name
              </label>
              <Input id="name" type="text" placeholder="Your name" disabled />
            </div>
          </div>
          <Button size="sm" disabled>
            Save account
          </Button>
        </CardContent>
      </Card>

      <Separator />

      <Card className="border-border">
        <CardHeader>
          <CardTitle className="text-base">Appearance</CardTitle>
          <CardDescription>
            Choose how Job Agent looks on your device.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ThemeAppearanceSettings />
        </CardContent>
      </Card>

      <Separator />

      <Card className="border-border">
        <CardHeader>
          <CardTitle className="text-base">AI preferences</CardTitle>
          <CardDescription>
            Customize how the agent interprets your search intent.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label htmlFor="search-prompt" className="text-sm font-medium">
              Default search prompt
            </label>
            <textarea
              id="search-prompt"
              rows={4}
              placeholder="e.g. Senior backend roles in Berlin, Python and FastAPI, remote-friendly…"
              disabled
              className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 disabled:cursor-not-allowed disabled:opacity-50"
            />
          </div>
          <div className="space-y-2">
            <label htmlFor="tone" className="text-sm font-medium">
              Outreach tone
            </label>
            <Input
              id="tone"
              type="text"
              placeholder="Professional and concise"
              disabled
            />
          </div>
          <Button size="sm" disabled>
            Save preferences
          </Button>
        </CardContent>
      </Card>

      <Separator />

      <Card className="border-destructive/30">
        <CardHeader>
          <div className="flex items-center gap-2">
            <AlertTriangle className="size-4 text-destructive" />
            <CardTitle className="text-base text-destructive">
              Danger zone
            </CardTitle>
          </div>
          <CardDescription>
            Irreversible actions for your account and data.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="space-y-1">
            <p className="text-sm font-medium">Delete account</p>
            <p className="text-sm text-muted-foreground">
              Permanently remove your account, CVs, and application history.
            </p>
          </div>
          <Button variant="destructive" size="sm" disabled>
            Delete account
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
