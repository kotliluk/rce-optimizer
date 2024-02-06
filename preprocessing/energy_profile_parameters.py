from typing_extensions import TypedDict

from utils.dict import get_nested

DIR_TYPES = ['side', 'into_dist', 'from_afar', 'up', 'down']


class CommonParameters(TypedDict):
    robot_weight_coef: float
    payload_weight_coef: float


class IdlingParameters(TypedDict):
    base: float

    dist_coef__A: float
    dist_coef__B: float
    dist_coef__C: float

    height_coef__A: float
    height_coef__B: float
    height_coef__C: float


class MovementParameters(TypedDict):
    base: float

    type_factor__side: float
    type_factor__into_dist: float
    type_factor__from_afar: float
    type_factor__up: float
    type_factor__down: float

    length_coef__side__A: float
    length_coef__side__B: float
    length_coef__side__C: float
    length_coef__into_dist__A: float
    length_coef__into_dist__B: float
    length_coef__into_dist__C: float
    length_coef__from_afar__A: float
    length_coef__from_afar__B: float
    length_coef__from_afar__C: float
    length_coef__up__A: float
    length_coef__up__B: float
    length_coef__up__C: float
    length_coef__down__A: float
    length_coef__down__B: float
    length_coef__down__C: float

    avg_dist_coef__side__A: float
    avg_dist_coef__side__B: float
    avg_dist_coef__side__C: float
    avg_dist_coef__into_dist__A: float
    avg_dist_coef__into_dist__B: float
    avg_dist_coef__into_dist__C: float
    avg_dist_coef__from_afar__A: float
    avg_dist_coef__from_afar__B: float
    avg_dist_coef__from_afar__C: float
    avg_dist_coef__up__A: float
    avg_dist_coef__up__B: float
    avg_dist_coef__up__C: float
    avg_dist_coef__down__A: float
    avg_dist_coef__down__B: float
    avg_dist_coef__down__C: float

    avg_height_coef__side__A: float
    avg_height_coef__side__B: float
    avg_height_coef__side__C: float
    avg_height_coef__into_dist__A: float
    avg_height_coef__into_dist__B: float
    avg_height_coef__into_dist__C: float
    avg_height_coef__from_afar__A: float
    avg_height_coef__from_afar__B: float
    avg_height_coef__from_afar__C: float
    avg_height_coef__up__A: float
    avg_height_coef__up__B: float
    avg_height_coef__up__C: float
    avg_height_coef__down__A: float
    avg_height_coef__down__B: float
    avg_height_coef__down__C: float


class OptMovementParameters(MovementParameters):
    # default shift of the left point of optimal duration segment (used as: left_dur_shift * apr_opt_dur), value (0, 1)
    left_dur_shift: float
    # min ratio used for the left point of optimal duration segment (used as: min_left_dur_ratio * min_dur), value > 1
    # as left point of opt duration segment is set MAX(left_dur_shift * apr_opt_dur, min_left_dur_ratio * min_dur)
    min_left_dur_ratio: float
    # default shift of the right point of optimal duration segment (used as: right_dur_shift * apr_opt_dur), value > 1
    right_dur_shift: float
    # min ratio used for the right point of optimal duration segment (used as: min_right_dur_ratio * min_dur), value > 1
    # as right point of opt duration segment is set MAX(right_dur_shift * apr_opt_dur, min_right_dur_ratio * min_dur)
    min_right_dur_ratio: float


class MovementsParameters(TypedDict):
    min_duration: MovementParameters
    max_duration: MovementParameters
    opt_duration: OptMovementParameters


class EnergyProfileParameters(TypedDict):
    common: CommonParameters
    idling: IdlingParameters
    movement: MovementsParameters


# parameter values obtained by best behavior in optimization on a Kuka KR16R2010 in Process Simulate
DEFAULT_PARAMETERS_MANUAL: EnergyProfileParameters = {
    'common': {
        'robot_weight_coef': (1/100)*(1/3),
        'payload_weight_coef': (1/100),
    },
    # parameters obtained by minimization of maximum error on a Kuka KR16R2010 in Process Simulate
    'idling': {
        'base': 459.467,

        'dist_coef__A': 0.0000000498495596354268,
        'dist_coef__B': -0.0000572767214878698,
        'dist_coef__C': 0.967112983697484,

        'height_coef__A': 0.0000000101273980243634,
        'height_coef__B': -0.0000145216802956174,
        'height_coef__C': 1.02632067389933,
    },
    # parameters obtained by minimization of sum of squared relative errors on a Kuka KR16R2010 in Process Simulate
    'movement': {
        'min_duration': {
            'base': 173.93394017094002,
            'type_factor__side': 0.8304592815053654,
            'type_factor__into_dist': 0.7523440604387334,
            'type_factor__from_afar': 0.7217361974991551,
            'type_factor__up': 0.5570466762401072,
            'type_factor__down': 0.6885993433649472,
            'length_coef__side__A': -2.9642058539157175e-06,
            'length_coef__side__B': 0.005170183259193887,
            'length_coef__side__C': -0.6039355575352781,
            'length_coef__into_dist__A': -1.2147259191963273e-06,
            'length_coef__into_dist__B': 0.0027298755180599032,
            'length_coef__into_dist__C': 0.007727839372655851,
            'length_coef__from_afar__A': -5.290186194420041e-07,
            'length_coef__from_afar__B': 0.0019443656827270303,
            'length_coef__from_afar__C': 0.1707696195715016,
            'length_coef__up__A': -1.2812446606360528e-06,
            'length_coef__up__B': 0.003280825086579991,
            'length_coef__up__C': -0.22531357595831952,
            'length_coef__down__A': -1.5075825020147378e-06,
            'length_coef__down__B': 0.0037777800450758603,
            'length_coef__down__C': -0.3817241099642636,
            'avg_dist_coef__side__A': -4.4677528887673986e-07,
            'avg_dist_coef__side__B': 0.00084803985737865,
            'avg_dist_coef__side__C': 0.6747352279592053,
            'avg_dist_coef__into_dist__A': -9.768530016563226e-07,
            'avg_dist_coef__into_dist__B': 0.002095578903308267,
            'avg_dist_coef__into_dist__C': 0.0,
            'avg_dist_coef__from_afar__A': -8.423119029821208e-07,
            'avg_dist_coef__from_afar__B': 0.0019089682126513078,
            'avg_dist_coef__from_afar__C': 0.0,
            'avg_dist_coef__up__A': 9.774488857407347e-07,
            'avg_dist_coef__up__B': -0.0028967618679811777,
            'avg_dist_coef__up__C': 2.825937207946747,
            'avg_dist_coef__down__A': 7.859703351674412e-07,
            'avg_dist_coef__down__B': -0.002309844513382708,
            'avg_dist_coef__down__C': 2.437003464512027,
            'avg_height_coef__side__A': 9.157644771760709e-07,
            'avg_height_coef__side__B': -0.0013831899524788787,
            'avg_height_coef__side__C': 1.3316240080934618,
            'avg_height_coef__into_dist__A': -1.1122278257558422e-06,
            'avg_height_coef__into_dist__B': 0.0024293098606983916,
            'avg_height_coef__into_dist__C': 0.42279912246484375,
            'avg_height_coef__from_afar__A': -2.1439118401072976e-06,
            'avg_height_coef__from_afar__B': 0.003317773991711929,
            'avg_height_coef__from_afar__C': 0.41122750430682026,
            'avg_height_coef__up__A': -1.9868386519448283e-06,
            'avg_height_coef__up__B': 0.0010598481125079502,
            'avg_height_coef__up__C': 1.4149882808306034,
            'avg_height_coef__down__A': -2.3885919858410494e-06,
            'avg_height_coef__down__B': 0.0013148904673710548,
            'avg_height_coef__down__C': 1.5006227995428523,
        },
        'max_duration': {
            'base': 768.6196752136756,
            'type_factor__side': 0.6375234569419244,
            'type_factor__into_dist': 1.0973431111314016,
            'type_factor__from_afar': 1.042682274430861,
            'type_factor__up': 0.7841074397098696,
            'type_factor__down': 0.6223300095674174,
            'length_coef__side__A': -3.11675015658237e-07,
            'length_coef__side__B': 0.002278554255236644,
            'length_coef__side__C': -0.041156290346181595,
            'length_coef__into_dist__A': -1.2550312834968866e-06,
            'length_coef__into_dist__B': 0.002992167694936335,
            'length_coef__into_dist__C': -0.10280439726646332,
            'length_coef__from_afar__A': 3.8127599867267855e-07,
            'length_coef__from_afar__B': 0.0011238215245326377,
            'length_coef__from_afar__C': 0.2865799833893496,
            'length_coef__up__A': -2.7046725322600904e-07,
            'length_coef__up__B': 0.0019557824468962983,
            'length_coef__up__C': 0.09057690249750028,
            'length_coef__down__A': -9.07662692572206e-07,
            'length_coef__down__B': 0.0028417845227866802,
            'length_coef__down__C': -0.13155074862111715,
            'avg_dist_coef__side__A': 1.1413836313650712e-06,
            'avg_dist_coef__side__B': -0.0036602844447858655,
            'avg_dist_coef__side__C': 3.4691636095543896,
            'avg_dist_coef__into_dist__A': -5.308328528617122e-07,
            'avg_dist_coef__into_dist__B': 0.0014803931808831604,
            'avg_dist_coef__into_dist__C': 0.0,
            'avg_dist_coef__from_afar__A': -3.1935435592859235e-07,
            'avg_dist_coef__from_afar__B': 0.0011924890509260283,
            'avg_dist_coef__from_afar__C': 0.0,
            'avg_dist_coef__up__A': -7.080543559930304e-07,
            'avg_dist_coef__up__B': 0.0007670191381389747,
            'avg_dist_coef__up__C': 1.1014545164500924,
            'avg_dist_coef__down__A': -8.389020720580897e-07,
            'avg_dist_coef__down__B': 0.0006136560658423143,
            'avg_dist_coef__down__C': 1.4755884841535556,
            'avg_height_coef__side__A': -1.9363077105015392e-07,
            'avg_height_coef__side__B': 0.0003348468656968612,
            'avg_height_coef__side__C': 0.9152289812223459,
            'avg_height_coef__into_dist__A': 1.4695860845016462e-06,
            'avg_height_coef__into_dist__B': -0.0021480476669584877,
            'avg_height_coef__into_dist__C': 1.5072080264804686,
            'avg_height_coef__from_afar__A': 1.619231607733128e-06,
            'avg_height_coef__from_afar__B': -0.0024183666995296177,
            'avg_height_coef__from_afar__C': 1.5938522333157692,
            'avg_height_coef__up__A': 3.2227831260085265e-06,
            'avg_height_coef__up__B': -0.003842396486083208,
            'avg_height_coef__up__C': 1.678307485220305,
            'avg_height_coef__down__A': 3.4284740969056094e-06,
            'avg_height_coef__down__B': -0.0036871530627402417,
            'avg_height_coef__down__C': 1.5132190562138426,
        },
        'opt_duration': {
            'base': 1.3213076923076923,
            'type_factor__side': 0.9794066838757486,
            'type_factor__into_dist': 1.0257176774405121,
            'type_factor__from_afar': 1.014094399040341,
            'type_factor__up': 0.9715283110647733,
            'type_factor__down': 1.0299151663343438,
            'length_coef__side__A': -2.519723762568115e-07,
            'length_coef__side__B': 0.0005458466836102875,
            'length_coef__side__C': 0.7943312216331696,
            'length_coef__into_dist__A': -1.507681334060624e-07,
            'length_coef__into_dist__B': 0.0002780047763772004,
            'length_coef__into_dist__C': 0.9041758736211971,
            'length_coef__from_afar__A': -1.3876755212627732e-07,
            'length_coef__from_afar__B': 0.0004247340213900292,
            'length_coef__from_afar__C': 0.8159032969367234,
            'length_coef__up__A': -4.2380280670018055e-07,
            'length_coef__up__B': 0.0007818903834080587,
            'length_coef__up__C': 0.7323843972889712,
            'length_coef__down__A': -5.604350867612998e-07,
            'length_coef__down__B': 0.0008555535493677917,
            'length_coef__down__C': 0.7475639114467866,
            'avg_dist_coef__side__A': 5.1413247728091436e-09,
            'avg_dist_coef__side__B': -8.378128026706676e-05,
            'avg_dist_coef__side__C': 1.0782330367725441,
            'avg_dist_coef__into_dist__A': -6.383979642039558e-07,
            'avg_dist_coef__into_dist__B': 0.0016278183739822918,
            'avg_dist_coef__into_dist__C': 0.0,
            'avg_dist_coef__from_afar__A': -6.685443507454593e-07,
            'avg_dist_coef__from_afar__B': 0.0016692485752077375,
            'avg_dist_coef__from_afar__C': 0.0,
            'avg_dist_coef__up__A': 7.29137961320792e-08,
            'avg_dist_coef__up__B': -0.00029099776718130224,
            'avg_dist_coef__up__C': 1.2077036329352264,
            'avg_dist_coef__down__A': 7.659466871910321e-08,
            'avg_dist_coef__down__B': -0.00030778141027286616,
            'avg_dist_coef__down__C': 1.2204280612407565,
            'avg_height_coef__side__A': 1.4359761331777498e-07,
            'avg_height_coef__side__B': -0.0002153964199766625,
            'avg_height_coef__side__C': 1.0484295226412925,
            'avg_height_coef__into_dist__A': -8.334310472905604e-08,
            'avg_height_coef__into_dist__B': 0.00017220562036732135,
            'avg_height_coef__into_dist__C': 0.9493386763839499,
            'avg_height_coef__from_afar__A': -2.6357433711892743e-07,
            'avg_height_coef__from_afar__B': 0.00028356898240881315,
            'avg_height_coef__from_afar__C': 0.9685483071871877,
            'avg_height_coef__up__A': -1.359720726517706e-07,
            'avg_height_coef__up__B': 4.3268678026634254e-05,
            'avg_height_coef__up__C': 1.035880489337657,
            'avg_height_coef__down__A': -8.363173067012508e-08,
            'avg_height_coef__down__B': 2.5691927117600266e-05,
            'avg_height_coef__down__C': 1.0223325863675738,
            'left_dur_shift': 0.9,
            'min_left_dur_ratio': 1.1,
            'right_dur_shift': 1.1,
            'min_right_dur_ratio': 1.3,
        },
    },
}


def _p(custom: EnergyProfileParameters, default: EnergyProfileParameters, name: str):
    given_value = get_nested(custom, name)
    return given_value if given_value is not None else get_nested(default, name)


def merge_parameters(c: EnergyProfileParameters, d: EnergyProfileParameters) -> EnergyProfileParameters:
    """
    Merge given parameters dictionaries. First, uses value from the given custom parameters "c", if not found,
    uses value from the given default parameters "d".
    """
    return {
        'common': {
            'robot_weight_coef': _p(c, d, 'common.robot_weight_coef'),
            'payload_weight_coef': _p(c, d, 'common.payload_weight_coef'),
        },
        'idling': {
            'base': _p(c, d, 'idling.base'),

            'dist_coef__A': _p(c, d, 'idling.dist_coef__A'),
            'dist_coef__B': _p(c, d, 'idling.dist_coef__B'),
            'dist_coef__C': _p(c, d, 'idling.dist_coef__C'),

            'height_coef__A': _p(c, d, 'idling.height_coef__A'),
            'height_coef__B': _p(c, d, 'idling.height_coef__B'),
            'height_coef__C': _p(c, d, 'idling.height_coef__C'),
        },
        'movement': {
            'min_duration': {
                'base': _p(c, d, 'movement.min_duration.base'),

                'type_factor__side': _p(c, d, 'movement.min_duration.type_factor__side'),
                'type_factor__into_dist': _p(c, d, 'movement.min_duration.type_factor__into_dist'),
                'type_factor__from_afar': _p(c, d, 'movement.min_duration.type_factor__from_afar'),
                'type_factor__up': _p(c, d, 'movement.min_duration.type_factor__up'),
                'type_factor__down': _p(c, d, 'movement.min_duration.type_factor__down'),

                'length_coef__side__A': _p(c, d, 'movement.min_duration.length_coef__side__A'),
                'length_coef__side__B': _p(c, d, 'movement.min_duration.length_coef__side__B'),
                'length_coef__side__C': _p(c, d, 'movement.min_duration.length_coef__side__C'),
                'length_coef__into_dist__A': _p(c, d, 'movement.min_duration.length_coef__into_dist__A'),
                'length_coef__into_dist__B': _p(c, d, 'movement.min_duration.length_coef__into_dist__B'),
                'length_coef__into_dist__C': _p(c, d, 'movement.min_duration.length_coef__into_dist__C'),
                'length_coef__from_afar__A': _p(c, d, 'movement.min_duration.length_coef__from_afar__A'),
                'length_coef__from_afar__B': _p(c, d, 'movement.min_duration.length_coef__from_afar__B'),
                'length_coef__from_afar__C': _p(c, d, 'movement.min_duration.length_coef__from_afar__C'),
                'length_coef__up__A': _p(c, d, 'movement.min_duration.length_coef__up__A'),
                'length_coef__up__B': _p(c, d, 'movement.min_duration.length_coef__up__B'),
                'length_coef__up__C': _p(c, d, 'movement.min_duration.length_coef__up__C'),
                'length_coef__down__A': _p(c, d, 'movement.min_duration.length_coef__down__A'),
                'length_coef__down__B': _p(c, d, 'movement.min_duration.length_coef__down__B'),
                'length_coef__down__C': _p(c, d, 'movement.min_duration.length_coef__down__C'),

                'avg_dist_coef__side__A': _p(c, d, 'movement.min_duration.avg_dist_coef__side__A'),
                'avg_dist_coef__side__B': _p(c, d, 'movement.min_duration.avg_dist_coef__side__B'),
                'avg_dist_coef__side__C': _p(c, d, 'movement.min_duration.avg_dist_coef__side__C'),
                'avg_dist_coef__into_dist__A': _p(c, d, 'movement.min_duration.avg_dist_coef__into_dist__A'),
                'avg_dist_coef__into_dist__B': _p(c, d, 'movement.min_duration.avg_dist_coef__into_dist__B'),
                'avg_dist_coef__into_dist__C': _p(c, d, 'movement.min_duration.avg_dist_coef__into_dist__C'),
                'avg_dist_coef__from_afar__A': _p(c, d, 'movement.min_duration.avg_dist_coef__from_afar__A'),
                'avg_dist_coef__from_afar__B': _p(c, d, 'movement.min_duration.avg_dist_coef__from_afar__B'),
                'avg_dist_coef__from_afar__C': _p(c, d, 'movement.min_duration.avg_dist_coef__from_afar__C'),
                'avg_dist_coef__up__A': _p(c, d, 'movement.min_duration.avg_dist_coef__up__A'),
                'avg_dist_coef__up__B': _p(c, d, 'movement.min_duration.avg_dist_coef__up__B'),
                'avg_dist_coef__up__C': _p(c, d, 'movement.min_duration.avg_dist_coef__up__C'),
                'avg_dist_coef__down__A': _p(c, d, 'movement.min_duration.avg_dist_coef__down__A'),
                'avg_dist_coef__down__B': _p(c, d, 'movement.min_duration.avg_dist_coef__down__B'),
                'avg_dist_coef__down__C': _p(c, d, 'movement.min_duration.avg_dist_coef__down__C'),

                'avg_height_coef__side__A': _p(c, d, 'movement.min_duration.avg_height_coef__side__A'),
                'avg_height_coef__side__B': _p(c, d, 'movement.min_duration.avg_height_coef__side__B'),
                'avg_height_coef__side__C': _p(c, d, 'movement.min_duration.avg_height_coef__side__C'),
                'avg_height_coef__into_dist__A': _p(c, d, 'movement.min_duration.avg_height_coef__into_dist__A'),
                'avg_height_coef__into_dist__B': _p(c, d, 'movement.min_duration.avg_height_coef__into_dist__B'),
                'avg_height_coef__into_dist__C': _p(c, d, 'movement.min_duration.avg_height_coef__into_dist__C'),
                'avg_height_coef__from_afar__A': _p(c, d, 'movement.min_duration.avg_height_coef__from_afar__A'),
                'avg_height_coef__from_afar__B': _p(c, d, 'movement.min_duration.avg_height_coef__from_afar__B'),
                'avg_height_coef__from_afar__C': _p(c, d, 'movement.min_duration.avg_height_coef__from_afar__C'),
                'avg_height_coef__up__A': _p(c, d, 'movement.min_duration.avg_height_coef__up__A'),
                'avg_height_coef__up__B': _p(c, d, 'movement.min_duration.avg_height_coef__up__B'),
                'avg_height_coef__up__C': _p(c, d, 'movement.min_duration.avg_height_coef__up__C'),
                'avg_height_coef__down__A': _p(c, d, 'movement.min_duration.avg_height_coef__down__A'),
                'avg_height_coef__down__B': _p(c, d, 'movement.min_duration.avg_height_coef__down__B'),
                'avg_height_coef__down__C': _p(c, d, 'movement.min_duration.avg_height_coef__down__C'),
            },
            'max_duration': {
                'base': _p(c, d, 'movement.max_duration.base'),

                'type_factor__side': _p(c, d, 'movement.max_duration.type_factor__side'),
                'type_factor__into_dist': _p(c, d, 'movement.max_duration.type_factor__into_dist'),
                'type_factor__from_afar': _p(c, d, 'movement.max_duration.type_factor__from_afar'),
                'type_factor__up': _p(c, d, 'movement.max_duration.type_factor__up'),
                'type_factor__down': _p(c, d, 'movement.max_duration.type_factor__down'),

                'length_coef__side__A': _p(c, d, 'movement.max_duration.length_coef__side__A'),
                'length_coef__side__B': _p(c, d, 'movement.max_duration.length_coef__side__B'),
                'length_coef__side__C': _p(c, d, 'movement.max_duration.length_coef__side__C'),
                'length_coef__into_dist__A': _p(c, d, 'movement.max_duration.length_coef__into_dist__A'),
                'length_coef__into_dist__B': _p(c, d, 'movement.max_duration.length_coef__into_dist__B'),
                'length_coef__into_dist__C': _p(c, d, 'movement.max_duration.length_coef__into_dist__C'),
                'length_coef__from_afar__A': _p(c, d, 'movement.max_duration.length_coef__from_afar__A'),
                'length_coef__from_afar__B': _p(c, d, 'movement.max_duration.length_coef__from_afar__B'),
                'length_coef__from_afar__C': _p(c, d, 'movement.max_duration.length_coef__from_afar__C'),
                'length_coef__up__A': _p(c, d, 'movement.max_duration.length_coef__up__A'),
                'length_coef__up__B': _p(c, d, 'movement.max_duration.length_coef__up__B'),
                'length_coef__up__C': _p(c, d, 'movement.max_duration.length_coef__up__C'),
                'length_coef__down__A': _p(c, d, 'movement.max_duration.length_coef__down__A'),
                'length_coef__down__B': _p(c, d, 'movement.max_duration.length_coef__down__B'),
                'length_coef__down__C': _p(c, d, 'movement.max_duration.length_coef__down__C'),

                'avg_dist_coef__side__A': _p(c, d, 'movement.max_duration.avg_dist_coef__side__A'),
                'avg_dist_coef__side__B': _p(c, d, 'movement.max_duration.avg_dist_coef__side__B'),
                'avg_dist_coef__side__C': _p(c, d, 'movement.max_duration.avg_dist_coef__side__C'),
                'avg_dist_coef__into_dist__A': _p(c, d, 'movement.max_duration.avg_dist_coef__into_dist__A'),
                'avg_dist_coef__into_dist__B': _p(c, d, 'movement.max_duration.avg_dist_coef__into_dist__B'),
                'avg_dist_coef__into_dist__C': _p(c, d, 'movement.max_duration.avg_dist_coef__into_dist__C'),
                'avg_dist_coef__from_afar__A': _p(c, d, 'movement.max_duration.avg_dist_coef__from_afar__A'),
                'avg_dist_coef__from_afar__B': _p(c, d, 'movement.max_duration.avg_dist_coef__from_afar__B'),
                'avg_dist_coef__from_afar__C': _p(c, d, 'movement.max_duration.avg_dist_coef__from_afar__C'),
                'avg_dist_coef__up__A': _p(c, d, 'movement.max_duration.avg_dist_coef__up__A'),
                'avg_dist_coef__up__B': _p(c, d, 'movement.max_duration.avg_dist_coef__up__B'),
                'avg_dist_coef__up__C': _p(c, d, 'movement.max_duration.avg_dist_coef__up__C'),
                'avg_dist_coef__down__A': _p(c, d, 'movement.max_duration.avg_dist_coef__down__A'),
                'avg_dist_coef__down__B': _p(c, d, 'movement.max_duration.avg_dist_coef__down__B'),
                'avg_dist_coef__down__C': _p(c, d, 'movement.max_duration.avg_dist_coef__down__C'),

                'avg_height_coef__side__A': _p(c, d, 'movement.max_duration.avg_height_coef__side__A'),
                'avg_height_coef__side__B': _p(c, d, 'movement.max_duration.avg_height_coef__side__B'),
                'avg_height_coef__side__C': _p(c, d, 'movement.max_duration.avg_height_coef__side__C'),
                'avg_height_coef__into_dist__A': _p(c, d, 'movement.max_duration.avg_height_coef__into_dist__A'),
                'avg_height_coef__into_dist__B': _p(c, d, 'movement.max_duration.avg_height_coef__into_dist__B'),
                'avg_height_coef__into_dist__C': _p(c, d, 'movement.max_duration.avg_height_coef__into_dist__C'),
                'avg_height_coef__from_afar__A': _p(c, d, 'movement.max_duration.avg_height_coef__from_afar__A'),
                'avg_height_coef__from_afar__B': _p(c, d, 'movement.max_duration.avg_height_coef__from_afar__B'),
                'avg_height_coef__from_afar__C': _p(c, d, 'movement.max_duration.avg_height_coef__from_afar__C'),
                'avg_height_coef__up__A': _p(c, d, 'movement.max_duration.avg_height_coef__up__A'),
                'avg_height_coef__up__B': _p(c, d, 'movement.max_duration.avg_height_coef__up__B'),
                'avg_height_coef__up__C': _p(c, d, 'movement.max_duration.avg_height_coef__up__C'),
                'avg_height_coef__down__A': _p(c, d, 'movement.max_duration.avg_height_coef__down__A'),
                'avg_height_coef__down__B': _p(c, d, 'movement.max_duration.avg_height_coef__down__B'),
                'avg_height_coef__down__C': _p(c, d, 'movement.max_duration.avg_height_coef__down__C'),
            },
            'opt_duration': {
                'base': _p(c, d, 'movement.opt_duration.base'),

                'type_factor__side': _p(c, d, 'movement.opt_duration.type_factor__side'),
                'type_factor__into_dist': _p(c, d, 'movement.opt_duration.type_factor__into_dist'),
                'type_factor__from_afar': _p(c, d, 'movement.opt_duration.type_factor__from_afar'),
                'type_factor__up': _p(c, d, 'movement.opt_duration.type_factor__up'),
                'type_factor__down': _p(c, d, 'movement.opt_duration.type_factor__down'),

                'length_coef__side__A': _p(c, d, 'movement.opt_duration.length_coef__side__A'),
                'length_coef__side__B': _p(c, d, 'movement.opt_duration.length_coef__side__B'),
                'length_coef__side__C': _p(c, d, 'movement.opt_duration.length_coef__side__C'),
                'length_coef__into_dist__A': _p(c, d, 'movement.opt_duration.length_coef__into_dist__A'),
                'length_coef__into_dist__B': _p(c, d, 'movement.opt_duration.length_coef__into_dist__B'),
                'length_coef__into_dist__C': _p(c, d, 'movement.opt_duration.length_coef__into_dist__C'),
                'length_coef__from_afar__A': _p(c, d, 'movement.opt_duration.length_coef__from_afar__A'),
                'length_coef__from_afar__B': _p(c, d, 'movement.opt_duration.length_coef__from_afar__B'),
                'length_coef__from_afar__C': _p(c, d, 'movement.opt_duration.length_coef__from_afar__C'),
                'length_coef__up__A': _p(c, d, 'movement.opt_duration.length_coef__up__A'),
                'length_coef__up__B': _p(c, d, 'movement.opt_duration.length_coef__up__B'),
                'length_coef__up__C': _p(c, d, 'movement.opt_duration.length_coef__up__C'),
                'length_coef__down__A': _p(c, d, 'movement.opt_duration.length_coef__down__A'),
                'length_coef__down__B': _p(c, d, 'movement.opt_duration.length_coef__down__B'),
                'length_coef__down__C': _p(c, d, 'movement.opt_duration.length_coef__down__C'),

                'avg_dist_coef__side__A': _p(c, d, 'movement.opt_duration.avg_dist_coef__side__A'),
                'avg_dist_coef__side__B': _p(c, d, 'movement.opt_duration.avg_dist_coef__side__B'),
                'avg_dist_coef__side__C': _p(c, d, 'movement.opt_duration.avg_dist_coef__side__C'),
                'avg_dist_coef__into_dist__A': _p(c, d, 'movement.opt_duration.avg_dist_coef__into_dist__A'),
                'avg_dist_coef__into_dist__B': _p(c, d, 'movement.opt_duration.avg_dist_coef__into_dist__B'),
                'avg_dist_coef__into_dist__C': _p(c, d, 'movement.opt_duration.avg_dist_coef__into_dist__C'),
                'avg_dist_coef__from_afar__A': _p(c, d, 'movement.opt_duration.avg_dist_coef__from_afar__A'),
                'avg_dist_coef__from_afar__B': _p(c, d, 'movement.opt_duration.avg_dist_coef__from_afar__B'),
                'avg_dist_coef__from_afar__C': _p(c, d, 'movement.opt_duration.avg_dist_coef__from_afar__C'),
                'avg_dist_coef__up__A': _p(c, d, 'movement.opt_duration.avg_dist_coef__up__A'),
                'avg_dist_coef__up__B': _p(c, d, 'movement.opt_duration.avg_dist_coef__up__B'),
                'avg_dist_coef__up__C': _p(c, d, 'movement.opt_duration.avg_dist_coef__up__C'),
                'avg_dist_coef__down__A': _p(c, d, 'movement.opt_duration.avg_dist_coef__down__A'),
                'avg_dist_coef__down__B': _p(c, d, 'movement.opt_duration.avg_dist_coef__down__B'),
                'avg_dist_coef__down__C': _p(c, d, 'movement.opt_duration.avg_dist_coef__down__C'),

                'avg_height_coef__side__A': _p(c, d, 'movement.opt_duration.avg_height_coef__side__A'),
                'avg_height_coef__side__B': _p(c, d, 'movement.opt_duration.avg_height_coef__side__B'),
                'avg_height_coef__side__C': _p(c, d, 'movement.opt_duration.avg_height_coef__side__C'),
                'avg_height_coef__into_dist__A': _p(c, d, 'movement.opt_duration.avg_height_coef__into_dist__A'),
                'avg_height_coef__into_dist__B': _p(c, d, 'movement.opt_duration.avg_height_coef__into_dist__B'),
                'avg_height_coef__into_dist__C': _p(c, d, 'movement.opt_duration.avg_height_coef__into_dist__C'),
                'avg_height_coef__from_afar__A': _p(c, d, 'movement.opt_duration.avg_height_coef__from_afar__A'),
                'avg_height_coef__from_afar__B': _p(c, d, 'movement.opt_duration.avg_height_coef__from_afar__B'),
                'avg_height_coef__from_afar__C': _p(c, d, 'movement.opt_duration.avg_height_coef__from_afar__C'),
                'avg_height_coef__up__A': _p(c, d, 'movement.opt_duration.avg_height_coef__up__A'),
                'avg_height_coef__up__B': _p(c, d, 'movement.opt_duration.avg_height_coef__up__B'),
                'avg_height_coef__up__C': _p(c, d, 'movement.opt_duration.avg_height_coef__up__C'),
                'avg_height_coef__down__A': _p(c, d, 'movement.opt_duration.avg_height_coef__down__A'),
                'avg_height_coef__down__B': _p(c, d, 'movement.opt_duration.avg_height_coef__down__B'),
                'avg_height_coef__down__C': _p(c, d, 'movement.opt_duration.avg_height_coef__down__C'),

                'left_dur_shift': _p(c, d, 'movement.opt_duration.left_dur_shift'),
                'min_left_dur_ratio': _p(c, d, 'movement.opt_duration.min_left_dur_ratio'),
                'right_dur_shift': _p(c, d, 'movement.opt_duration.right_dur_shift'),
                'min_right_dur_ratio': _p(c, d, 'movement.opt_duration.min_right_dur_ratio'),
            },
        },
    }
