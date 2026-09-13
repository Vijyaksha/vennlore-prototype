export interface Loc {
  building: string | null;
  room: string | null;
}

export interface Connection {
  walk: number;
  slack: number;
  tight: boolean;
}

const SAME_ROOM = 5;
const SAME_CLUSTER_SAME_FLOOR = 10;
const SAME_BUILDING = 15;
const CROSS_BUILDING = 22;
const OFFSITE = 60;
const UNKNOWN = 15;
const TIGHT_SLACK = 15;

// Rooms follow "<cluster words> <number-ish suffix>": the cluster is the run of
// leading purely-alphabetic words ("Bluebird 2C" -> "Bluebird", "Exhibit Hall
// D, E & F, Level 2" -> "Exhibit Hall"), the floor the first digit after it.
function parseRoom(room: string): { cluster: string; floor: string | null } {
  const words: string[] = [];
  for (const token of room.split(/\s+/)) {
    if (!/^[A-Za-z]{2,}$/.test(token)) break;
    words.push(token);
  }
  const cluster = words.join(" ");
  const floor = /\d/.exec(room.slice(cluster.length))?.[0] ?? null;
  return { cluster, floor };
}

export function walkMinutes(a: Loc, b: Loc): number {
  if (
    a.building !== null &&
    a.room !== null &&
    a.building === b.building &&
    a.room === b.room
  ) {
    return SAME_ROOM;
  }
  if (a.building === "Offsite" || b.building === "Offsite") {
    return OFFSITE;
  }
  if (a.building === null || b.building === null) {
    return UNKNOWN;
  }
  // A known cross-building trip must never be underestimated, so the building
  // comparison outranks the null-room fallback.
  if (a.building !== b.building) {
    return CROSS_BUILDING;
  }
  if (a.room === null || b.room === null) {
    return UNKNOWN;
  }
  const roomA = parseRoom(a.room);
  const roomB = parseRoom(b.room);
  if (
    roomA.cluster !== "" &&
    roomA.cluster === roomB.cluster &&
    roomA.floor === roomB.floor
  ) {
    return SAME_CLUSTER_SAME_FLOOR;
  }
  return SAME_BUILDING;
}

export function connection(gapMinutes: number, walk: number): Connection {
  const slack = gapMinutes - walk;
  return { walk, slack, tight: slack < TIGHT_SLACK };
}
