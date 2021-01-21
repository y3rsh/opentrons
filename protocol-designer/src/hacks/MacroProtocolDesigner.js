// @flow
import * as React from 'react'

import {
  useProtocolSession,
  useCreateProtocolSession,
  useMoveToWell,
} from './api'

import { Flex, Box } from '@opentrons/components'
import { CommandList } from './CommandList'
import { ClickableDeckMap } from './ClickableDeckMap'

import type { Command } from './command-types'
import type { LabwareData } from './labware-types'
import type { Highlight } from './ui-types'

export function MacroProtocolDesigner(): React.Node {
  const [highlights, setHighlights] = React.useState<Array<Highlight>>([])
  const session = useProtocolSession('localhost')
  const createSession = useCreateProtocolSession('localhost')
  const moveToWell = useMoveToWell('localhost')

  const commands: Array<Command> = session?.details.commands ?? []
  const labware: Array<LabwareData> = session?.details.labware ?? []

  const handleCommandClick = commandId => {
    const command = commands.find(c => c.commandId === commandId)

    const labwareId =
      // $FlowFixMe: this is safe but flow doesn't like it
      command?.request.labwareId ?? command?.result?.labwareId ?? null

    // $FlowFixMe: this is safe but flow doesn't like it
    const wellName = command?.request.wellName ?? null

    setHighlights([{ commandId, labwareId, wellName }])
  }

  const handleWellClick = (labwareId, wellName) => {
    console.log(labwareId, wellName)
    moveToWell({ labwareId, wellName })
  }

  return (
    <>
      {session == null ? (
        <button onClick={() => createSession()}>Start session</button>
      ) : null}
      <Flex flexDirection="row">
        <Box width="16rem">
          <CommandList
            commands={commands}
            highlights={highlights}
            onCommandClick={handleCommandClick}
          />
        </Box>
        <Box maxWidth="64rem">
          <ClickableDeckMap
            labware={labware}
            highlights={highlights}
            onWellClick={handleWellClick}
          />
        </Box>
      </Flex>
    </>
  )
}
