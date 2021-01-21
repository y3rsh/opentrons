// @flow
import * as React from 'react'
import { Text, C_BLACK, C_BLUE } from '@opentrons/components'

import type { Command } from './command-types'
import type { Highlight } from './ui-types'

export type CommandListProps = {|
  commands: Array<Command>,
  highlights: Array<Highlight>,
  onCommandClick: (commandId: string) => mixed,
|}

export function CommandList(props: CommandListProps): React.Node {
  const { commands, highlights, onCommandClick } = props

  return (
    <ul>
      {commands.map(command => {
        const { commandId } = command
        const color = highlights.some(h => h.commandId === commandId)
          ? C_BLUE
          : C_BLACK

        return (
          <li key={commandId} onClick={() => onCommandClick(commandId)}>
            <Text color={color}>{commandId}</Text>
          </li>
        )
      })}
    </ul>
  )
}
