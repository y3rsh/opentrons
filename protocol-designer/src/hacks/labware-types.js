// @flow

import type { LabwareDefinition2 } from '@opentrons/shared-data'

export type { LabwareDefinition2 as LabwareDefinition }

export type LabwareLocation = {
  slot: number,
  ...
}

export type LabwareData = {
  labware_id: string,
  definition: LabwareDefinition2,
  location: LabwareLocation,
  ...
}
