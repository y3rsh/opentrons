import * as React from 'react'
import { pick } from 'lodash'
import { when } from 'jest-when'
import '@testing-library/jest-dom'
import { fireEvent } from '@testing-library/react'
import {
  anyProps,
  partialComponentPropsMatcher,
  renderWithProviders,
} from '@opentrons/components'
import noModulesProtocol from '@opentrons/shared-data/protocol/fixtures/4/simpleV4.json'
import withModulesProtocol from '@opentrons/shared-data/protocol/fixtures/4/testModulesProtocol.json'

import { i18n } from '../../../../i18n'
import {
  mockAttachedPipette,
  mockPipetteInfo,
} from '../../../../redux/pipettes/__fixtures__'
import { mockConnectedRobot } from '../../../../redux/discovery/__fixtures__'
import * as discoverySelectors from '../../../../redux/discovery/selectors'
import {
  getAttachedPipettes,
  getProtocolPipetteTipRackCalInfo,
} from '../../../../redux/pipettes'
import { mockCalibrationStatus } from '../../../../redux/calibration/__fixtures__'
import * as calibrationSelectors from '../../../../redux/calibration/selectors'
import { useProtocolCalibrationStatus } from '../../RunSetupCard/hooks/useProtocolCalibrationStatus'
import { useProtocolDetails } from '../../../RunDetails/hooks'
import { RunSetupCard } from '../../RunSetupCard'
import { ModuleSetup } from '../../RunSetupCard/ModuleSetup'
import { LabwareSetup } from '../../RunSetupCard/LabwareSetup'
import { RobotCalibration } from '../../RunSetupCard/RobotCalibration'
import { ProceedToRunCta } from '../../RunSetupCard/ProceedToRunCta'

import type {
  AttachedPipettesByMount,
  ProtocolPipetteTipRackCalDataByMount,
} from '../../../../redux/pipettes/types'

jest.mock('../../../../redux/discovery/selectors')
jest.mock('../../../../redux/pipettes/selectors')
jest.mock('../../../../redux/calibration/selectors')
jest.mock('../../RunSetupCard/hooks/useProtocolCalibrationStatus')
jest.mock('../../../RunDetails/hooks')
jest.mock('../../RunSetupCard/LabwareSetup')
jest.mock('../../RunSetupCard/ModuleSetup')
jest.mock('../../RunSetupCard/RobotCalibration')
jest.mock('../../RunSetupCard/ProceedToRunCta')

const mockAttachedPipettes: AttachedPipettesByMount = {
  left: mockAttachedPipette,
  right: null,
} as any

const mockProtocolPipetteTipRackCalData: ProtocolPipetteTipRackCalDataByMount = {
  left: mockPipetteInfo,
  right: null,
} as any

const mockUseProtocolDetails = useProtocolDetails as jest.MockedFunction<
  typeof useProtocolDetails
>
const mockLabwareSetup = LabwareSetup as jest.MockedFunction<
  typeof LabwareSetup
>
const mockModuleSetup = ModuleSetup as jest.MockedFunction<typeof ModuleSetup>
const mockRobotCalibration = RobotCalibration as jest.MockedFunction<
  typeof RobotCalibration
>
const mockProceedToRun = ProceedToRunCta as jest.MockedFunction<
  typeof ProceedToRunCta
>
const mockGetConnectedRobot = discoverySelectors.getConnectedRobot as jest.MockedFunction<
  typeof discoverySelectors.getConnectedRobot
>
const mockGetAttachedPipettes = getAttachedPipettes as jest.MockedFunction<
  typeof getAttachedPipettes
>

const mockGetProtocolPipetteTiprackData = getProtocolPipetteTipRackCalInfo as jest.MockedFunction<
  typeof getProtocolPipetteTipRackCalInfo
>

const mockGetDeckCalData = calibrationSelectors.getDeckCalibrationData as jest.MockedFunction<
  typeof calibrationSelectors.getDeckCalibrationData
>

const mockUseProtocolCalibrationStatus = useProtocolCalibrationStatus as jest.MockedFunction<
  typeof useProtocolCalibrationStatus
>

const render = () => {
  return renderWithProviders(<RunSetupCard />, { i18nInstance: i18n })[0]
}

describe('RunSetupCard', () => {
  beforeEach(() => {
    mockGetConnectedRobot.mockReturnValue(mockConnectedRobot)
    mockGetAttachedPipettes.mockReturnValue(mockAttachedPipettes)
    mockGetProtocolPipetteTiprackData.mockReturnValue(
      mockProtocolPipetteTipRackCalData
    )
    mockGetDeckCalData.mockReturnValue(
      mockCalibrationStatus.deckCalibration.data
    )
    mockUseProtocolCalibrationStatus.mockReturnValue({ complete: true })
    mockUseProtocolDetails.mockReturnValue({
      protocolData: noModulesProtocol,
    } as any)

    mockLabwareSetup.mockReturnValue(<div>Mock Labware Setup</div>)

    when(mockModuleSetup)
      .mockReturnValue(<div></div>) // this (default) empty div will be returned when ModuleSetup isn't called with expected props
      .calledWith(
        partialComponentPropsMatcher({
          expandLabwareSetupStep: expect.anything(),
          robotName: mockConnectedRobot.name,
        })
      )
      .mockImplementation(({ expandLabwareSetupStep }) => (
        <div onClick={expandLabwareSetupStep}>Mock Module Setup</div>
      ))
    when(mockRobotCalibration)
      .mockReturnValue(<div></div>) // this (default) empty div will be returned when RobotCalibration isn't called with expected props
      .calledWith(
        partialComponentPropsMatcher({
          robot: mockConnectedRobot,
        })
      )
      .mockReturnValue(<div>Mock Robot Calibration</div>)

    when(mockProceedToRun)
      .mockReturnValue(<div></div>)
      // @ts-expect-error need to provide anyProps bcuz under the hood react calls components with arguments even when they dont take props
      .calledWith(anyProps())
      .mockReturnValue(<div>Mock Proceed To Run</div>)
  })

  afterEach(() => {
    jest.resetAllMocks()
  })

  describe('when no modules are in the protocol', () => {
    it('renders robot calibration heading', () => {
      const { getByRole } = render()
      getByRole('heading', {
        name: 'Robot Calibration',
      })
    })
    it('renders calibration needed when robot cal not complete', () => {
      mockUseProtocolCalibrationStatus.mockReturnValue({ complete: false })
      const { getByText } = render()
      getByText('Calibration needed')
    })
    it('renders labware setup', () => {
      const { getByRole, getByText } = render()
      const labwareSetup = getByRole('heading', { name: 'Labware Setup' })
      fireEvent.click(labwareSetup)
      getByText('Mock Labware Setup')
    })
    it('does NOT render module setup', () => {
      const { queryByText } = render()
      expect(queryByText(/module setup/i)).toBeNull()
    })
  })

  it('renders module setup and allows the user to proceed to labware setup', () => {
    mockUseProtocolDetails.mockReturnValue({
      protocolData: withModulesProtocol,
    } as any)

    const { getByRole, getByText } = render()
    const moduleSetupHeading = getByRole('heading', { name: 'Module Setup' })
    fireEvent.click(moduleSetupHeading)
    const moduleSetup = getByText('Mock Module Setup')
    fireEvent.click(moduleSetup)
    getByText('Mock Labware Setup')
  })
  it('renders correct text contents for multiple modules', () => {
    mockUseProtocolDetails.mockReturnValue({
      protocolData: withModulesProtocol,
    } as any)
    const { getByRole, getByText } = render()
    expect(getByRole('heading', { name: 'Setup for Run' })).toBeTruthy()
    expect(getByRole('heading', { name: 'STEP 1' })).toBeTruthy()
    expect(getByRole('heading', { name: 'Robot Calibration' })).toBeTruthy()
    expect(
      getByText(
        'Review required pipettes and tip length calibrations for this protocol.'
      )
    ).toBeTruthy()
    expect(getByRole('heading', { name: 'STEP 2' })).toBeTruthy()
    expect(getByRole('heading', { name: 'Labware Setup' })).toBeTruthy()
    expect(
      getByText(
        'Position full tip racks and labware in the deck slots as shown in the deck map.'
      )
    ).toBeTruthy()
    expect(getByRole('heading', { name: 'STEP 3' })).toBeTruthy()
    expect(getByRole('heading', { name: 'Module Setup' })).toBeTruthy()
    expect(
      getByText(
        'Plug in and turn on the required modules via the OT-2 USB Ports. Place the modules as shown in the deck map.'
      )
    ).toBeTruthy()
  })
  it('renders correct text contents for single module', () => {
    mockUseProtocolDetails.mockReturnValue({
      protocolData: {
        ...withModulesProtocol,
        modules: pick(
          withModulesProtocol.modules,
          Object.keys(withModulesProtocol.modules)[0]
        ),
      },
    } as any)
    const { getByRole, getByText } = render()
    expect(getByRole('heading', { name: 'Setup for Run' })).toBeTruthy()
    expect(getByRole('heading', { name: 'STEP 1' })).toBeTruthy()
    expect(getByRole('heading', { name: 'Robot Calibration' })).toBeTruthy()
    expect(
      getByText(
        'Review required pipettes and tip length calibrations for this protocol.'
      )
    ).toBeTruthy()
    expect(getByRole('heading', { name: 'STEP 2' })).toBeTruthy()
    expect(getByRole('heading', { name: 'Module Setup' })).toBeTruthy()
    expect(
      getByText(
        'Plug in and turn on the required module via the OT-2 USB Port. Place the module as shown in the deck map.'
      )
    ).toBeTruthy()
    expect(getByRole('heading', { name: 'STEP 3' })).toBeTruthy()
    expect(getByRole('heading', { name: 'Labware Setup' })).toBeTruthy()
    expect(
      getByText(
        'Position full tip racks and labware in the deck slots as shown in the deck map.'
      )
    ).toBeTruthy()
  })
  it('if no modules renders robot calibration heading, skips module setup, renders labware setup heading, and allows the user to proceed to run', () => {
    const { getByRole, getByText } = render()
    getByRole('heading', {
      name: 'Robot Calibration',
    })
    getByRole('heading', {
      name: 'Labware Setup',
    })
    const proceedToRun = getByText('Mock Proceed To Run')
    fireEvent.click(proceedToRun)
    getByText('Mock Proceed To Run')
  })
  it('defaults to labware step expanded if calibration complete and no modules present', async () => {
    mockUseProtocolDetails.mockReturnValue({
      protocolData: noModulesProtocol,
    } as any)

    const { queryByText, getByText } = render()
    await new Promise(resolve => setTimeout(resolve, 1000))
    expect(getByText('Mock Labware Setup')).toBeVisible()
    expect(queryByText(/mock module setup/i)).toBeNull()
  })
  it('defaults to module step expanded if calibration complete and modules present', async () => {
    mockUseProtocolDetails.mockReturnValue({
      protocolData: withModulesProtocol,
    } as any)

    const { queryByText, getByText } = render()
    await new Promise(resolve => setTimeout(resolve, 1000))
    expect(getByText('Mock Module Setup')).toBeVisible()
    expect(queryByText(/mock labware setup/i)).not.toBeVisible()
  })
  it('defaults to robot cal expanded if calibration incomplete and no modules present', async () => {
    mockUseProtocolDetails.mockReturnValue({
      protocolData: noModulesProtocol,
    } as any)
    mockUseProtocolCalibrationStatus.mockReturnValue({ complete: false })

    const { queryByText, getByText } = render()
    await new Promise(resolve => setTimeout(resolve, 1000))
    expect(getByText('Mock Robot Calibration')).toBeVisible()
    expect(queryByText(/mock labware setup/i)).not.toBeVisible()
  })
  it('defaults to robot cal expanded if calibration incomplete and modules present', async () => {
    mockUseProtocolDetails.mockReturnValue({
      protocolData: withModulesProtocol,
    } as any)
    mockUseProtocolCalibrationStatus.mockReturnValue({ complete: false })

    const { queryByText, getByText } = render()
    await new Promise(resolve => setTimeout(resolve, 1000))
    expect(getByText('Mock Robot Calibration')).toBeVisible()
    expect(queryByText(/mock module setup/i)).not.toBeVisible()
  })
})
