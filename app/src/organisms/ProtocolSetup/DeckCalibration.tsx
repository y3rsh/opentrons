import * as React from 'react'
import { useSelector } from 'react-redux'
import { useTranslation } from 'react-i18next'
import { Text, SPACING_3 } from '@opentrons/components'
import type { State } from '../../redux/types'
import * as Calibration from '../../redux/calibration'
import type { DeckCalibrationData } from '../../redux/calibration/types'
import { formatLastModified } from '../../organisms/CalibrationPanels/utils'

interface Props {
  robotName: string
}

export function DeckCalibration(props: Props): JSX.Element | null {
  const { robotName } = props
  const { t } = useTranslation(['robot_calibration', 'shared'])

  const deckCalData: DeckCalibrationData | null = useSelector(
    (state: State) => {
      return Calibration.getDeckCalibrationData(state, robotName)
    }
  )

  // this component's parent should never be rendered if there is no deckCalData
  if (deckCalData == null) {
    return null
  }

  const buildDeckLastCalibrated: (
    deckCalData: DeckCalibrationData
  ) => string = deckCalData => {
    const datestring =
      'lastModified' in deckCalData &&
      typeof deckCalData.lastModified === 'string'
        ? formatLastModified(deckCalData.lastModified)
        : t('shared:unknown')
    const getPrefix = (calData: DeckCalibrationData): string =>
      'source' in calData && typeof calData?.source === 'string'
        ? 'source' in calData &&
          calData.source === Calibration.CALIBRATION_SOURCE_LEGACY
          ? t('last_migrated')
          : t('last_calibrated')
        : t('last_calibrated')

    return `${getPrefix(deckCalData)}: ${datestring}`
  }
  return (
    <div>
      <Text marginTop={SPACING_3}>Deck Calibration</Text>
      <div>{buildDeckLastCalibrated(deckCalData)}</div>
    </div>
  )
}
