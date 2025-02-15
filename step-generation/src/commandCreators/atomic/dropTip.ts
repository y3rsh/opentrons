import { FIXED_TRASH_ID } from '../../constants'
import type { Command } from '@opentrons/shared-data/protocol/types/schemaV5Addendum'
import type { CommandCreator } from '../../types'
interface DropTipArgs {
  pipette: string
}

/** Drop tip if given pipette has a tip. If it has no tip, do nothing. */
export const dropTip: CommandCreator<DropTipArgs> = (
  args,
  invariantContext,
  prevRobotState
) => {
  const { pipette } = args

  // No-op if there is no tip
  if (!prevRobotState.tipState.pipettes[pipette]) {
    return {
      commands: [],
    }
  }

  const commands: Command[] = [
    {
      command: 'dropTip',
      params: {
        pipette,
        labware: FIXED_TRASH_ID,
        well: 'A1', // TODO: Is 'A1' of the trash always the right place to drop tips?
      },
    },
  ]
  return {
    commands,
  }
}
