// @flow
import * as React from 'react'

import { getAllDefinitions } from '../labware-defs/utils'

import { Flex } from '@opentrons/components'
import { CommandList } from './CommandList'
import { ClickableDeckMap } from './ClickableDeckMap'

import type { Command } from './command-types'
import type { LabwareData } from './labware-types'
import type { Highlight } from './ui-types'

const labwareDefs = getAllDefinitions()

const labware: Array<LabwareData> = [
  {
    labware_id: 'labware-1',
    definition: labwareDefs['opentrons/nest_96_wellplate_200ul_flat/1'],
    location: { slot: 5 },
  },
  {
    labware_id: 'labware-2',
    definition: labwareDefs['opentrons/agilent_1_reservoir_290ml/1'],
    location: { slot: 2 },
  },
]

const commands: Array<Command> = [
  {
    command_type: 'loadLabware',
    command_id: 'command-1',
    created_at: new Date().toISOString(),
    started_at: new Date().toISOString(),
    completed_at: new Date().toISOString(),
    request: {
      location: { slot: 5 },
      loadName: 'nest_96_wellplate_200ul_flat',
      namespace: 'opentrons',
      version: 1,
    },
    result: {
      labwareId: 'labware-1',
      definition: labwareDefs['opentrons/nest_96_wellplate_200ul_flat/1'],
      calibration: [0, 0, 0],
    },
  },
  {
    command_type: 'moveToWell',
    command_id: 'command-2',
    created_at: new Date().toISOString(),
    started_at: new Date().toISOString(),
    completed_at: new Date().toISOString(),
    request: {
      pipetteId: 'pipette-1',
      labwareId: 'labware-1',
      wellName: 'B2',
    },
    result: {},
  },
  {
    command_type: 'moveToWell',
    command_id: 'command-3',
    created_at: new Date().toISOString(),
    started_at: new Date().toISOString(),
    completed_at: new Date().toISOString(),
    request: {
      pipetteId: 'pipette-1',
      labwareId: 'labware-2',
      wellName: 'A1',
    },
    result: {},
  },
]

export function HackApp(): React.Node {
  const [highlights, setHighlights] = React.useState<Array<Highlight>>([])

  const handleCommandClick = commandId => {
    const command = commands.find(c => c.command_id === commandId)

    const labwareId =
      // $FlowFixMe: this is safe but flow doesn't like it
      command?.request.labwareId ?? command?.result?.labwareId ?? null

    // $FlowFixMe: this is safe but flow doesn't like it
    const wellName = command?.request.wellName ?? null

    setHighlights([{ commandId, labwareId, wellName }])
  }

  const handleWellClick = (labwareId, wellName) => {
    console.log(labwareId, wellName)
  }

  return (
    <Flex flexDirection="row">
      <CommandList
        commands={commands}
        highlights={highlights}
        onCommandClick={handleCommandClick}
      />
      <ClickableDeckMap
        labware={labware}
        highlights={highlights}
        onWellClick={handleWellClick}
      />
    </Flex>
  )
}
