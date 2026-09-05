import { NextResponse } from "next/server";
import { authOptions } from "@/lib/auth";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const envCheck = {
    has_DISCORD_CLIENT_ID: Boolean(process.env.DISCORD_CLIENT_ID),
    has_DISCORD_CLIENT_SECRET: Boolean(process.env.DISCORD_CLIENT_SECRET),
    has_NEXTAUTH_SECRET: Boolean(process.env.NEXTAUTH_SECRET),
    has_NEXTAUTH_URL: Boolean(process.env.NEXTAUTH_URL),
    NEXTAUTH_URL_value: process.env.NEXTAUTH_URL || null,
    NODE_ENV: process.env.NODE_ENV,
    VERCEL_ENV: process.env.VERCEL_ENV || null,
  };

  try {
    const url = new URL(request.url);
    return NextResponse.json({
      status: "ok",
      envCheck,
      url: url.origin,
      providers: authOptions.providers.map((p: any) => ({
        id: p.id,
        name: p.name,
        type: p.type
      }))
    });
  } catch (err: any) {
    return NextResponse.json({
      status: "error",
      envCheck,
      message: err?.message
    }, { status: 500 });
  }
}
