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
        const { command_id, command_type } = command
        const color = highlights.some(h => h.commandId === command_id)
          ? C_BLUE
          : C_BLACK

        return (
          <li key={command_id} onClick={() => onCommandClick(command_id)}>
            <Text color={color}>{command_type}</Text>
          </li>
        )
      })}
    </ul>
  )
}
