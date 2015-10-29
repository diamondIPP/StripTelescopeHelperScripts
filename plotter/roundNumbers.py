#! /usr/bin/python


def get_signifErrDigits(err) :
	err = abs(err)
	err_str = '%e' % err
	coeff = float(err_str.split('e')[0])
	if coeff < 3.55 :
		return 2
	else :
		return 1


def get_precision(num, err) :
	err_precision = get_signifErrDigits(err)
	precision = get_exponent(num) - get_exponent(err) + get_signifErrDigits(err)
	return [precision, err_precision]


def get_exponent(num) :
	num_str = '%e' % num
	exp = int(num_str.split('e')[1])
	return exp


def get_roundedNumber(num, err, rnd = None, float_digits = None) :
	if rnd == None :
		rnd = get_signifErrDigits(err) - get_exponent(err) - 1
	if float_digits == None :
		float_digits = rnd
	if float_digits < 0 : float_digits = 0
	num_str = format(round(num, rnd), '.%df' % float_digits)
	err_str = format(round(err, rnd), '.%df' % float_digits)
	return (num_str, err_str)


def get_roundedNumberErrors(num, errors) :
	'''returns tuple of strings with rounded value and uncertainties'''
	rnds = []
	err_str = []
	for err in errors :
		rnd = get_signifErrDigits(err) - get_exponent(err) - 1
		rnds.append(rnd)
		if rnd < 0 : float_digits = 0
		else       : float_digits = rnd
		err_str.append(format(round(err, rnd), '.%df' % float_digits))
	rnd = max(rnds)
	if rnd < 0 : float_digits = 0
	else       : float_digits = rnd
	num_str = format(round(num, rnd), '.%df' % float_digits)
	return (num_str,) + tuple(err_str)
