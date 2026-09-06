import { NextRequest, NextResponse } from 'next/server';
import lawsData from '@/data/laws_dataset.json';

export async function GET(
  _req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const idNum = parseInt(params.id, 10);
    const law = lawsData.central_acts.find((item: any) => item.id === idNum) ||
                lawsData.state_acts.find((item: any) => item.id === idNum);

    if (!law) {
      return NextResponse.json({ error: 'Law section not found' }, { status: 404 });
    }

    return NextResponse.json(law);
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
